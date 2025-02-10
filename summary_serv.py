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

from typing import Dict
import json

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
import torch
from ray import serve
from ray.serve.handle import DeploymentHandle
from ray.serve.schema import LoggingConfig

from app.router import (
    DemoRouterIngress, SummaryRouterIngress, TranslationRouterIngress)
from app.src.engine import (LLMService, llm_ready)


app = FastAPI(
    title="Dencomm LLM Service",
    lifespan=llm_ready)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*", "/demo/*"],
    allow_methods=["*"],
    allow_headers=["*"])


@serve.deployment(num_replicas=1)
@serve.ingress(app=app)
class APIIngress(
    DemoRouterIngress, 
    SummaryRouterIngress, 
    TranslationRouterIngress):
    routing = False

    def __init__(
        self, 
        llm_handle: DeploymentHandle = None,
    ) -> None:
        super().__init__(llm_handle=llm_handle)

        self.server_logger.info("""
            ####################
            #  Server Started  #
            ####################
        """)
        self.server_logger.info(app.routes)

        # 추가 라우터가 있으면 계속 등록
        for cls in self.__class__.mro():
            if hasattr(cls, "routing"):
                cls.service = self.service
                cls.service_as_stream = self.service_as_stream
                cls.register_routes(self=cls)
                app.include_router(
                    cls.router,
                    prefix=cls.prefix,
                    tags=cls.tags,
                    include_in_schema=cls.include_in_schema)
                self.server_logger.info(f"Routing {cls.__name__} to Application Updated")

                
    @app.get("/health")
    async def healthcheck(self,):
        try:
            return Response(
                content=json.dumps({"message": "ok"}),
                media_type="application/json",
                status_code=200)
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
        http_options={"host": "0.0.0.0", "port": cli_args.get("port", 8507)},
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
        # route_prefix="/"
        ).bind(
            llm_handle=LLMService.bind()
        )
