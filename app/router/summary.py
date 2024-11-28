import os

import logging
from typing import Any, List, Dict
import time
import traceback
import requests

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse, Response
from ray import serve
from ray.serve.handle import DeploymentHandle

from app.src.engine import OpenAIService, get_gpt_service
from app.dto import SummaryRequest, SummaryResponse
from app.utils.text_process import text_preprocess, text_postprocess
from app.logger import get_logger


router = APIRouter(prefix="/summary", tags=["summary"])
router_logger = get_logger()


@serve.deployment()
@serve.ingress(app=router)
class SummaryRouterIngress:
    def __init__(
        self, 
        llm_handle: DeploymentHandle = None
        ) -> None:
        if llm_handle is not None:
            self.service = llm_handle
        self.demo_address = "192.168.1.55:8504"
 
    @serve.batch(
        max_batch_size=4, 
        batch_wait_timeout_s=0.1)
    async def batched_summary(
        self, 
        request_prompt: List[Any],
        request_text: List[Any]
    ) -> List[str]:
        router_logger.info(f"Batched request: {len(request_text)}")
        return await self.service.summarize.remote(
            input_prompt=request_prompt,
            input_text=request_text,
            batch=True)
    
    @router.get("/health")
    async def healthcheck(
        self,
    ):
        try:
            return {"message": "ok"}
        except Exception as e:
            router_logger.error("error" + e)
            return Response(
                    content=f"Summary Service Can not Reply",
                    status_code=500
                )

    @router.post(
        "/gemma", 
        response_model=SummaryResponse)
    async def summarize(
        self,
        request: SummaryRequest,
        # service: LLMService = Depends(get_llm_service)
    ) -> SummaryResponse:
        result = ""
        # Generate predicted tokens
        try:
            # ----------------------------------- #
            st = time.time()
            # result += ray.get(service.summarize.remote(ray.put(request.text)))
            # assert len(request.text ) > 200, "Text is too short"
            result += await self.batched_summary(
                request_prompt=request.prompt,
                request_text=text_preprocess(request.text))
            # result = text_postprocess(result)
            # print(result)
            end = time.time()
            # ----------------------------------- #
            assert len(result) > 0, "Generation failed"
            print(f"Time: {end - st}")
        except AssertionError as e:
            result += e
        except Exception as e:
            print(traceback.format_exc())
            router_logger.error("error" + e)
            result += "Generation failed"
        finally:
            return SummaryResponse(text=result)

    @router.post(
        "/stream",
    )
    async def summarize_stream(
        self,
        request: SummaryRequest,
        # service: LLMService = Depends(get_llm_service)
    ):
        result = ""
        # Generate predicted tokens
        try:
            # ----------------------------------- #
            st = time.time()
            # result += ray.get(service.summarize.remote(ray.put(request.text)))
            # assert len(request.text ) > 200, "Text is too short"
            return StreamingResponse(
                content=self.service.summarize.remote(
                    input_prompt=request.prompt,
                    input_text=request.text, 
                    stream=True),
                media_type="text/event-stream")
            end = time.time()
            # ----------------------------------- #
            print(f"Time: {end - st}")
        except AssertionError as e:
            result += e
        except Exception as e:
            print(traceback.format_exc())
            router_logger.error("error" + e)
            result += "Error in summarize"


    @router.post(
        "/", 
        response_model=SummaryResponse)
    async def summarize_gpt(
        self,
        request: SummaryRequest,
        service: OpenAIService = Depends(get_gpt_service)
    ) -> SummaryResponse:
        result = ""
        try:
            # ----------------------------------- #
            st = time.time()
            # result += ray.get(service.summarize.remote(ray.put(request.text)))
            # assert len(request.text ) > 200, "Text is too short"
            input_text = text_preprocess(request.text)
            result += await service.summarize(
                input_prompt=request.prompt,
                input_text=input_text)
            # result = text_postprocess(result)
            # print(result)
            end = time.time()
            # ----------------------------------- #
            # print(f"Time: {end - st}")
        except AssertionError as e:
            router_logger.warn("error" + e)
            result += e
        except Exception as e:
            router_logger.warn("error" + e)
            result += "Error in summarize"
        finally:
            return SummaryResponse(text=result)

    @serve.batch(
        max_batch_size=4, 
        batch_wait_timeout_s=0.1)
    async def batched_generation(
        self, 
        request_prompt: List[Any],
        request_text: List[Any],
        source_language: str,
        detect_language: str,
        target_language: str,
        history: List[str],
        is_summary:bool = False
    ) -> List[str]:
        router_logger.info(f"Batched request: {len(request_text)}")
        if is_summary:
            return await self.service.translate_summarize.remote(
                input_prompt=request_prompt,
                input_text=request_text,
                history=history,
                source_language=source_language,
                detect_language=detect_language,
                target_language=target_language,
                batch=True)
        else:
            return await self.service.translate.remote(
                input_prompt=request_prompt,
                input_text=request_text,
                history=history,
                source_language=source_language,
                detect_language=detect_language,
                target_language=target_language,
                batch=True)
