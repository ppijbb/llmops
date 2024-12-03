import os

import logging
from typing import Any, List, Dict
import time
import traceback
import requests

from fastapi import APIRouter, Depends, FastAPI
from fastapi.responses import Response

from ray import serve
from ray.serve.handle import DeploymentHandle

from app.src.engine import OpenAIService, get_gpt_service
from app.dto import SummaryResponse
from app.dto import TranslateRequest, TranslateResponse
from app.utils.text_process import text_preprocess, text_postprocess
from app.utils.lang_detect import detect_language
from app.logger import get_logger


router = APIRouter()


# @serve.deployment
# @serve.ingress(app=router)
class TranslationRouterIngress:
    def __init__(
        self, 
        llm_handle: DeploymentHandle = None
        ) -> None:
        if llm_handle is not None:
            self.service = llm_handle
        self.demo_address = "192.168.1.55:8504"
        self.server_logger = get_logger()

    @router.get("/health")
    async def healthcheck(
        self,
    ):
        try:
            return {"message": "ok"}
        except Exception as e:
            self.server_logger.error("error" + e)
            return Response(
                    content=f"Translation Service Can not Reply",
                    status_code=500
                )

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
        self.server_logger.info(f"Batched request: {len(request_text)}")
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

    @router.post(
        "/gemma", 
        description='''
language code

    - ko : Korean
    - en : English
    - zh : Chinese
    - fr : French
    - es : Spanish
    
        ''',
        response_model=TranslateResponse)
    async def translate(
        self,
        request: TranslateRequest,
        # service: LLMService = Depends(get_llm_service)
    ) -> TranslateResponse:
        result = ""
        # Generate predicted tokens

        try:
            # ----------------------------------- #
            st = time.time()
            # result += ray.get(service.summarize.remote(ray.put(request.text)))
            # assert len(request.text ) > 200, "Text is too short"
            result += await self.batched_generation(
                request_prompt=None,
                history=request.history,
                source_language=request.source_language.value,
                detect_language=detect_language(request.text),
                target_language=[lang.value for lang in request.target_language],
                request_text=f'{text_preprocess(request.text)}')
            result = text_postprocess(result)
            # print(result)
            end = time.time()
            # ----------------------------------- #
            assert len(result) > 0, "Generation failed"
            print(f"Time: {end - st}")
        except AssertionError as e:
            result += e
        except Exception as e:
            print(traceback.format_exc())
            self.server_logger.error("error" + e)
            result += "Generation failed"
        finally:
            return TranslateResponse(
                text=result,
                original_text=request.text,
                source_language=request.source_language.value,
                target_language=[lang.value for lang in request.target_language])

    @router.post(
        "/",
        description='''
 language code
 
    - Korean: ko
    - English: en
    - Chinese: zh
    - French: fr
    - Spanish: es
        ''',
        response_model=TranslateResponse)
    async def translate_gpt(
        self,
        request: TranslateRequest,
        service: OpenAIService = Depends(get_gpt_service)
    ) -> TranslateResponse:
        result = ""
        try:
            # ----------------------------------- #
            st = time.time()
            # result += ray.get(service.summarize.remote(ray.put(request.text)))
            # assert len(request.text ) > 200, "Text is too short"
            input_text = text_preprocess(request.text)
            result += await service.translate(
                input_prompt=None,
                history=request.history,
                detect_language=detect_language(input_text),
                source_language=request.source_language.value,
                target_language=[lang.value for lang in request.target_language],
                input_text=input_text)
            # result = text_postprocess(result)
            # print(result)
            end = time.time()
            # ----------------------------------- #
            print(f"Time: {end - st}")
        except AssertionError as e:
            self.server_logger.warn("error" + e)
            result += e
        except Exception as e:
            self.server_logger.warn("error" + e)
            result += "Error in summarize"
        finally:
            return TranslateResponse(
                text=result,
                original_text=request.text,
                source_language=request.source_language.value,
                target_language=[lang.value for lang in request.target_language])

    @router.post(
        "/legacy",
        description='''
 language code
 
    - Korean: ko
    - English: en
    - Chinese: zh
    - French: fr
    - Spanish: es
        ''',
        response_model=TranslateResponse)
    async def translate_legacy(
        self,
        request: TranslateRequest,
        service: OpenAIService = Depends(get_gpt_service)
    ) -> TranslateResponse:
        result = ""
        
        try:
            # ----------------------------------- #
            st = time.time()
            # result += ray.get(service.summarize.remote(ray.put(request.text)))
            # assert len(request.text ) > 200, "Text is too short"
            input_text = text_preprocess(request.text)
            result += await service.translate_legacy(
                input_prompt=None,
                history=request.history,
                detect_language=detect_language(input_text),
                source_language=request.source_language.value,
                target_language=[lang.value for lang in request.target_language],
                input_text=input_text)
            # result = text_postprocess(result)
            # print(result)
            end = time.time()
            # ----------------------------------- #
            print(f"Time: {end - st}")
        except AssertionError as e:
            self.server_logger.warn("error" + e)
            result += e
        except Exception as e:
            self.server_logger.warn("error" + e)
            result += "Error in summarize"
        finally:
            return TranslateResponse(
                text=result,
                original_text=request.text,
                source_language=request.source_language.value,
                target_language=[lang.value for lang in request.target_language])

    @router.post(
        "/gemma/summarize", 
        response_model=SummaryResponse)
    async def transcript(
        self,
        request: TranslateRequest,
        # service: LLMService = Depends(get_llm_service)
    ) -> SummaryResponse:
        result = ""
        # Generate predicted tokens
        try:
            # ----------------------------------- #
            st = time.time()
            # result += ray.get(service.summarize.remote(ray.put(request.text)))
            # assert len(request.text ) > 200, "Text is too short"
            result += await self.batched_generation(
                request_prompt=None,
                history=request.history,
                detect_language=detect_language(request.text),
                source_language=request.source_language.value,
                target_language=[lang.value for lang in request.target_language],
                request_text=text_preprocess(request.text),
                is_summary=True)
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
            self.server_logger.error("error" + e)
            result += "Generation failed"
        finally:
            return SummaryResponse(text=result)

    @router.post(
        "/summarize", 
        response_model=SummaryResponse)
    async def transcript_gpt(
        self,
        request: TranslateRequest,
        service: OpenAIService = Depends(get_gpt_service)
    ) -> SummaryResponse:
        result = ""
        try:
            # ----------------------------------- #
            st = time.time()
            # result += ray.get(service.summarize.remote(ray.put(request.text)))
            # assert len(request.text ) > 200, "Text is too short"
            input_text = text_preprocess(request.text)
            result += await service.translate_summarize(
                history=[],
                input_text=input_text,
                source_language=request.source_language.value,
                target_language=[lang.value for lang in request.target_language])
            # result = text_postprocess(result)
            # print(result)
            end = time.time()
            # ----------------------------------- #
            # print(f"Time: {end - st}")
        except AssertionError as e:
            self.server_logger.error("error" + e)
            result += e
        except Exception as e:
            self.server_logger.error("error" + e)
            result += "Error in summarize"
        finally:
            return SummaryResponse(text=result)
