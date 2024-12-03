import os

os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = "0"

# os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = "0"
# os.environ["OMP_NUM_THREADS"] = "2"
# os.environ["ENABLE_SDP_FUSION"] = "1"
# os.environ["SYCL_CACHE_PERSISTENT"] = "1"
# os.environ["SYCL_PI_LEVEL_ZERO_USE_IMMEDIATE_COMMANDLISTS"] = "1"
# os.environ["MKL_NUM_THREADS"] = "24"
# os.environ["KMP_BLOCKTIME"] = "1"
# os.environ["KMP_AFFINITY"] = "granularity=fine,compact,1,0"
# os.environ["KMP_SETTINGS"] = "1"
# os.environ["KMP_DUPLICATE_LIB_OK"] = "True"
# os.environ["DNNL_PRIMITIVE_CACHE_CAPACITY"] = "1024"

import logging
from typing import Any, List, Dict
import time
import traceback
import requests
import httpx
import websockets
import asyncio
from contextlib import asynccontextmanager


from fastapi import FastAPI, APIRouter
from fastapi.routing import APIRoute
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, Response
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Match, Route
import torch
from ray import serve
from ray.serve.schema import LoggingConfig
from ray.dag.class_node import ClassNode
from ray.serve.handle import DeploymentHandle

from app.router import (
    demo_router, summary_router, translation_router,
    DemoRouterIngress, SummaryRouterIngress, TranslationRouterIngress)
from app.src.engine import (
    LLMService, OpenAIService, llm_ready,
    get_llm_service, get_gpt_service)
from app.dto import SummaryRequest, SummaryResponse
from app.dto import TranslateRequest, TranslateResponse
from app.utils.text_process import text_preprocess, text_postprocess
from app.utils.lang_detect import detect_language
from app.logger import get_logger


@asynccontextmanager
async def startup_event(app: FastAPI):
    app.logger.info("""
    ####################
    #  Server Started  #
    ####################""")
    yield
    app.logger.info("""
    ####################
    #    Terminated    #
    ####################""")

app = FastAPI(
    title="Dencomm LLM Service",
    root_path="/api/v1",
    lifespan=llm_ready,
    routes=[demo_router, summary_router, translation_router],)

def initialize_app():
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.mount(
        path="/api/v1/demo", 
        app=demo_router, 
        name="demo")
    app.mount(
        path="/api/v1/summary", 
        app=summary_router, 
        name="sumamry")
    app.mount(
        path="/api/v1/translation", 
        app=translation_router, 
        name="translation")
    # app.include_router(
    #     router=demo_router,
    #     prefix="/api/v1/demo",
    #     tags=["Demo"],
    #     include_in_schema=False)
    # app.include_router(
    #     router=summary_router,
    #     prefix="/api/v1/summary",
    #     tags=["Summary"], 
    #     include_in_schema=True)
    # app.include_router(
    #     router=translation_router,
    #     prefix="/api/v1/translation",
    #     tags=["Translation"],
    #     include_in_schema=True)


@serve.deployment
@serve.ingress(app=app)
class APIIngress:
    def __init__(self) -> None:
        self.logger = get_logger()
    
    @app.get("/health")
    async def healthcheck(
        self,
    ) -> Response:
        try:
            return Response(
                content={"message": "ok"},
                status_code=200)
        except Exception as e:
            self.logger.error("error" + e)
            return Response(
                    content=f"Server Status Unhealthy",
                    status_code=500
                )


@serve.deployment
class IngressDeployment:
    def __init__(self, deployment_tuples: List[tuple[FastAPI, ClassNode]]) -> None:
        self.logger = get_logger()
        self.routers_handles = []
        for app, handle in deployment_tuples:
            for route in app.routes:
                if isinstance(route, (APIRoute, Route)):  # user defined routes are APIRoutes
                    self.routers_handles.append((route, handle))
        self.logger.info(self.routers_handles)
   
    async def __call__(self, request: Request) -> Any:
        """Find an APIRoute that routes the request. Send the request the accompanying handler."""
        self.logger.info(self.routers_handles)
        self.logger.info(request.scope)
        for api_route, handle in self.routers_handles:
            (match, _,) = api_route.matches(request.scope)
            # Example of route matching:
            # https://github.com/tiangolo/fastapi/blob/0.85.2/fastapi/routing.py#L309-L313
            if match == Match.FULL:
                self.logger.info(match)
                self.logger.info(handle)
                request.scope["app"] = api_route
                request.scope["auth"] = "" # TODO : auth management
                request.scope["session"] = "" # TODO : session management
                request.scope["user"] = "" # TODO : user management
                self.logger.info(f"request type : {type(request)}")
                ref = await handle.remote(request)
                self.logger.info(f"ref type : {type(ref)}")
                return ref
            elif match == Match.PARTIAL:
                self.logger.info(match)
                self.logger.info(handle)
                return Response(
                    content=f"Method Not Allowed",
                    status_code=405
                )        
        # Unmatched case, return 404
        return Response(
                content=f"Page Not Found",
                status_code=404
            )

def build_app(
    cli_args: Dict[str, str]
) -> serve.Application:
    llm_service = LLMService.bind()
    initialize_app()
    # Main Application
    main_application = IngressDeployment.options(
        name="dencomm_llm_service",
        placement_group_bundles=[{
            "CPU": 1.0, 
            "GPU": float(torch.cuda.is_available())/2
            }], 
        placement_group_strategy="STRICT_PACK",
        route_prefix="/api/v1"
        ).bind(
            deployment_tuples=[
                (app, APIIngress.options(
                    name="dencomm_llm_main",
                    route_prefix="/api/v1",
                    _internal=True).bind()),
                (demo_router,
                 DemoRouterIngress.options(
                    name="dencomm_llm_demo",
                    route_prefix="/api/v1/demo",
                    _internal=True).bind(llm_service)),
                (summary_router,
                 SummaryRouterIngress.options(
                    name="dencomm_llm_summary",
                    route_prefix="/api/v1/summary",
                    _internal=True).bind(llm_service)),
                (translation_router, 
                 TranslationRouterIngress.options(
                    name="dencomm_llm_translation",
                    route_prefix="/api/v1/translation",
                    _internal=True).bind(llm_service))
            ]
        )    
    serve.start(
        proxy_location="EveryNode", 
        http_options={"host": "0.0.0.0", "port": 8504},
        logging_config=LoggingConfig(
            log_level="INFO",
            logs_dir="./logs",)
        )
    
    return main_application
