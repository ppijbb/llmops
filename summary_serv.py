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

from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, Response
import torch
from ray import serve
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


app = FastAPI(
    title="Dencomm LLM Service",
    lifespan=llm_ready)
app.include_router(
    demo_router, 
    include_in_schema=False)
app.include_router(
    summary_router, 
    include_in_schema=True)
app.include_router(
    translation_router, 
    include_in_schema=True)
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*", "/demo/*"],
    allow_methods=["*"],
    allow_headers=["*"])


server_logger = get_logger()
server_logger.info("""
####################
#  Server Started  #
####################
""")
server_logger.info(app.routes)

@serve.deployment(num_replicas=1, route_prefix="/api/v1")
@serve.ingress(app=app)
class APIIngress:
    def __init__(
        self, 
        routers: List[DeploymentHandle],
        # llm_handle: DeploymentHandle = None
        ) -> None:
        # if llm_handle is not None:
        #     self.service = llm_handle
        self.demo_address = "192.168.1.55:8504"



    @app.get("/health")
    async def healthcheck(
        self,
    ):
        try:
            return {"message": "ok"}
        except Exception as e:
            server_logger.error("error" + e)
            return Response(
                    content=f"Server Status Unhealthy",
                    status_code=500
                )


def build_app(
    cli_args: Dict[str, str]
) -> serve.Application:
    llm_service = LLMService.bind()
    
    return APIIngress.options(
        placement_group_bundles=[{
            "CPU":1.0, 
            "GPU": float(torch.cuda.is_available())/2
            }], 
        placement_group_strategy="STRICT_PACK",
        ).bind(
            [
                DemoRouterIngress.bind(llm_service),
                SummaryRouterIngress.bind(llm_service),
                TranslationRouterIngress.bind(llm_service)
            ]
        )

serve.start(http_options={"host": "0.0.0.0", "port": 8501})
