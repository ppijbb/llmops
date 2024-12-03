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

from typing import Any, List, Dict
import time
import requests

from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
import torch
from ray import serve
from ray.serve.handle import DeploymentHandle
from ray.serve.schema import LoggingConfig

from app.router import (
    demo_router, summary_router, translation_router,
    DemoRouterIngress, SummaryRouterIngress, TranslationRouterIngress)
from app.src.engine import (LLMService, llm_ready)
from app.logger import get_logger


app = FastAPI(
    title="Dencomm LLM Service",
    lifespan=llm_ready)
app.include_router(
    demo_router, 
    prefix="/demo",
    tags=["Demo Proxy"],
    include_in_schema=False)
app.include_router(
    summary_router, 
    prefix="/summary", 
    tags=["Counseling Summary"],
    include_in_schema=True)
app.include_router(
    translation_router,
    prefix="/translation",
    tags=["Lecture Translation"],
    include_in_schema=True)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*", "/demo/*"],
    allow_methods=["*"],
    allow_headers=["*"])

@serve.deployment(num_replicas=1, route_prefix="/api/v1")
@serve.ingress(app=app)
class APIIngress(DemoRouterIngress, SummaryRouterIngress, TranslationRouterIngress):
    def __init__(
        self, 
        llm_handle: DeploymentHandle = None,
        ) -> None:
        super().__init__(llm_handle)
        self.demo_address = "192.168.1.55:8504"
        self.server_logger = get_logger()
        self.server_logger.info("""
        ####################
        #  Server Started  #
        ####################
        """)
        self.server_logger.info(app.routes)

    @app.get("/health")
    async def healthcheck(
        self,
    ):
        try:
            return {"message": "ok"}
        except Exception as e:
            self.server_logger.error("error" + e)
            return Response(
                    content=f"Server Status Unhealthy",
                    status_code=500
                )

def build_app(
    cli_args: Dict[str, str]
) -> serve.Application:

    serve.start(
        proxy_location="EveryNode", 
        http_options={"host": "0.0.0.0", "port": 8504},
        logging_config=LoggingConfig(
            log_level="INFO",
            logs_dir="./logs",)
        )
    
    return APIIngress.options(
        placement_group_bundles=[{
            "CPU":1.0, 
            "GPU": float(torch.cuda.is_available())/2
            }], 
        placement_group_strategy="STRICT_PACK",
        ).bind(
            llm_handle = LLMService.bind()
        )
