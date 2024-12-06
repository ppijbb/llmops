from abc import ABC
from typing import List
from logging import Logger
from fastapi import APIRouter
from ray.serve.handle import DeploymentHandle

from app.logger import get_logger


class BaseIngress(ABC):
    routing: bool
    prefix: str 
    tags: List[str]
    include_in_schema: bool
    server_logger: Logger = get_logger()
    
    def __init__(
        self, 
        llm_handle: DeploymentHandle = None
        ) -> None:
        self.service = llm_handle
    
    @classmethod
    def _get_class(cls):
        return cls
       
    def register_routes(self, router:APIRouter):
        self.router = router
        pass


from .demo import router as demo_router
from .summary import router as summary_router
from .translation import router as translation_router

from .demo import DemoRouterIngress
from .summary import SummaryRouterIngress
from .translation import TranslationRouterIngress
