import os
import sys
import re
import json
from typing import Any, List
import time
import traceback

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import Response

from ray import serve
from ray.serve.handle import DeploymentHandle

from app.src.service.engine import OpenAIService, get_gpt_service
from app.dto import SummaryResponse
from app.dto import TranslateRequest, TranslateResponse
from app.enum.transcript import TargetLanguages
from app.utils.text_process import text_preprocess, text_postprocess
from app.utils.lang_detect import detect_language
from app.router import BaseIngress
from app.dto import SentenceSplitRequest, SentenceSplitResponse



router = APIRouter()

# @serve.deployment
# @serve.ingress(app=router)


class TranslationRouterIngress(BaseIngress):
    routing = True
    prefix = "/translate"
    tags = ["Lecture Translation"]
    include_in_schema = True
    
    def __init__(
        self, 
        llm_handle: DeploymentHandle = None
    ) -> None:
        super().__init__(llm_handle=llm_handle)

    @serve.batch(
        max_batch_size=4, 
        batch_wait_timeout_s=0.1)
    async def batched_generation(
        self, 
        request_prompt: List[Any],
        request_text: List[Any],
        source_language: str,
        detect_language: str,
        target_language: str,   # 수정: List[str]로 변경
        history: List[str],
        is_summary:bool = False
    ) -> List[str]:
        self_class = self[0]._get_class() # ray batch wrapper 에서 self가 list로 들어옴
        if is_summary:
            return await self_class.service.translate_summarize.remote(
                input_prompt=request_prompt,
                input_text=request_text,
                history=history,
                source_language=source_language,
                detect_language=detect_language,
                target_language=target_language,
                batch=True)
        else:
            return await self_class.service.translate.remote(
                input_prompt=request_prompt,
                input_text=request_text,
                history=history,
                source_language=source_language,
                detect_language=detect_language,
                target_language=target_language,
                batch=True)

    def register_routes(self, router:APIRouter=router):
        self.router = router
        
        @router.get("/health")
        async def healthcheck():
            try:
                return Response(
                    content=json.dumps({"message": "ok"}),
                    media_type="application/json",
                    status_code=200)
            except Exception as e:
                self.server_logger.error("error" + e)
                return Response(
                        content=f"Translation Service Can not Reply",
                        status_code=500
                    )
            
        @router.post(
            "/split_sentences",
            description="텍스트를 문장 단위로 분리하는 API.\n\n"
                        "**SentenceSplitRequest**\n"
                        "   - text: 분리할 텍스트.\n\n"
                        "**SentenceSplitResponse**\n"
                        "   - splited_sentences(List[str]): 분리된 문장들의 리스트.\n"
                        "   - completed_sentences(str): 완성된 문장 .\n"
                        "   - uncompleted_sentences(str): 미완성된 문장.\n"
                        "   - translation_flag(bool): 번역 요청 플래그.\n",
            response_model=SentenceSplitResponse
        )
        async def split_sentences(request: SentenceSplitRequest):
            try:
                
                # 개행 및 제어 문자 정리
                return SentenceSplitResponse(
                    splited_sentences=await self.service.split_sentences.remote(request.text))

            except Exception as e:
                raise HTTPException(status_code=500, detail=f"서버 내부 오류: {str(e)}")

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
            request: TranslateRequest,
            # service: LLMService = Depends(get_llm_service)
        ) -> TranslateResponse:
            #result = ""
            # Generate predicted tokens

            try:
                # ----------------------------------- #
                st = time.time()
                # result += ray.get(service.summarize.remote(ray.put(request.text)))
                # assert len(request.text ) > 200, "Text is too short"
                generated_results  += await self.batched_generation(
                    self=self._get_class(),
                    request_prompt=None,
                    history=request.history,
                    source_language=request.source_language.value,
                    detect_language=detect_language(request.text),
                    target_language=[lang.value for lang in request.target_language],
                    request_text=f'{text_preprocess(request.text)}')
                result = text_postprocess(result)
                end = time.time()
                # ----------------------------------- 
                print("text_postprocess",result)
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
            "",
            description='''
    language code
    
        - Korean: ko
        - English: en
        - Chinese: zh
        - French: fr
        - Spanish: es
        - Italian: it
        - German: de
            ''',
            response_model=TranslateResponse)
        async def translate_gpt(
            request: TranslateRequest,
            service: OpenAIService = Depends(get_gpt_service)
        ) -> TranslateResponse:
            text = ""
            try:
                # ----------------------------------- #
                st = time.time()
                # result += ray.get(service.summarize.remote(ray.put(request.text)))
                # assert len(request.text ) > 200, "Text is too short"
                #print("router text")
                #print(request.text)
                input_text = text_preprocess(request.text)
                #print("request.history")
                #print(request.history)
                #print("detect_language")
                #print(detect_language(input_text))
                #print("source_language")
                #print(request.source_language)
                #print("target_language")
                #print([lang.value for lang in request.target_language])
                result = await service.translate(
                    input_prompt=None,
                    history=request.history,
                    detect_language=detect_language(input_text),
                    source_language=request.source_language.value,
                    target_language=[lang.value for lang in request.target_language],
                    input_text=input_text)
                #result = text_postprocess(result)
                end = time.time()
                #print("result")
                #print(result)
                # ----------------------------------- #
                print(f"Time: {end - st}")
            except AssertionError as e:
                self.server_logger.error("error" + e)
                text += e
            except Exception as e:
                self.server_logger.error("error" + e)
                text += "Error in summarize"
            finally:
                return TranslateResponse(
                    text=text,
                    original_text=request.text,
                    source_language=request.source_language.value,
                    target_language=[lang.value for lang in request.target_language],
                    translations=result)

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
                self.server_logger.error("error" + e)
                result += e
            except Exception as e:
                self.server_logger.error("error" + e)
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
                    self=self._get_class(),
                    request_prompt=None,
                    history=request.history,
                    detect_language=detect_language(request.text),
                    source_language=request.source_language.value,
                    # target_language=[lang.value for lang in request.target_language],
                    target_language=[TargetLanguages.get_language_name(lang.value) for lang in request.target_language],
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
                    # target_language=[lang.value for lang in request.target_language],
                    target_language=[TargetLanguages.get_language_name(lang.value) for lang in request.target_language])
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
            
