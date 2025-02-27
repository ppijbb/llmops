import json

from typing import Any, List
import time
import traceback

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse, Response

from ray import serve
from ray.serve.handle import DeploymentHandle

from app.src.engine import OpenAIService, get_gpt_service
from app.dto import SummaryRequest, SummaryResponse
from app.utils.text_process import text_preprocess
from app.router import BaseIngress

router = APIRouter()


# @serve.deployment
# @serve.ingress(app=router)
class SummaryRouterIngress(BaseIngress):
    routing = True
    prefix = "/summarize"
    tags = ["Counseling Summary"]
    include_in_schema = True
    
    def __init__(
        self, 
        llm_handle: DeploymentHandle = None
    ) -> None:
        super().__init__(llm_handle=llm_handle)
        
    @serve.batch(
            max_batch_size=4, 
            batch_wait_timeout_s=0.1)
    async def batched_summary(
       self,
       request_prompt: List[Any],
       request_text: List[Any],
       language: List[str]
    ) -> List[str]:
        self_class = self[0]._get_class() # ray batch wrapper 에서 self가 list로 들어옴
        self_class.server_logger.info(f"Batched request: {len(request_text)}")
        return await self_class.service.summarize.remote(
            input_prompt=request_prompt,
            input_text=request_text,
            language=language,
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
                        content=f"Summary Service Can not Reply",
                        status_code=500
                    )

        @router.post(
            "/gemma", 
            description=(
            "dencomm sLLM 상담 내역 텍스트 요약 API.\n\n"
            "**SummaryRequest**\n"
            "   - text: 요약할 텍스트.\n"
            "   - prompt: (선택 사항) 요약에 사용할 프롬프트. 지정하지 않으면 기본 요약 프롬프트 적용.\n"
            "   - language: (선택 사항) 요약 결과 언어. 지정하지 않으면 영어(en)로 요약.\n\n"
            "       language code\n"
            "           - Korean: ko\n"
            "           - English: en\n\n"
            "**SummaryResponse**\n"
            "   - text: 요약된 텍스트."),
            response_model=SummaryResponse)
        async def summarize(
            request: SummaryRequest,
        ) -> SummaryResponse:
            result = ""
            # Generate predicted tokens
            await self.batched_summary(
                    self=self._get_class(),
                    request_prompt=request.prompt,
                    request_text=text_preprocess(request.text),
                    language=request.language)
            try:
                # ----------------------------------- #
                st = time.time()
                # result += ray.get(service.summarize.remote(ray.put(request.text)))
                # assert len(request.text ) > 200, "Text is too short"
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
            "/stream",
            description=(
            "dencomm sLLM 상담 내역 텍스트 요약 API.\n\n"
            "**SummaryRequest**\n"
            "   - text: 요약할 텍스트.\n"
            "   - prompt: (선택 사항) 요약에 사용할 프롬프트. 지정하지 않으면 기본 요약 프롬프트 적용.\n"
            "   - language: (선택 사항) 요약 결과 언어. 지정하지 않으면 영어(en)로 요약.\n\n"
            "       language code\n"
            "           - Korean: ko\n"
            "           - English: en\n\n"
            "**Streaming Response**\n"
            "   - text: 요약된 텍스트. 모델에서 생성되는 단어마다 Streaming Response로 전달됨."),
        )
        async def summarize_stream(
            request: SummaryRequest,
        ):
            result = ""
            # Generate predicted tokens
            try:
                # ----------------------------------- #
                st = time.time()
                # result += ray.get(service.summarize.remote(ray.put(request.text)))
                # assert len(request.text ) > 200, "Text is too short"
                return StreamingResponse(
                    content=self.service_as_stream.summarize.remote(
                        input_prompt=request.prompt,
                        input_text=request.text,
                        language=request.language,
                        stream=True),
                    media_type="text/event-stream")
                end = time.time()
                # ----------------------------------- #
                print(f"Time: {end - st}")
            except AssertionError as e:
                result += e
            except Exception as e:
                print(traceback.format_exc())
                self.server_logger.error("error" + e)
                result += "Error in summarize"


        @router.post(
            "",
            description=(
            "상담 내역 텍스트 요약 API.\n\n"
            "**SummaryRequest**\n"
            "   - text: 요약할 텍스트.\n"
            "   - prompt: (선택 사항) 요약에 사용할 프롬프트. 지정하지 않으면 기본 요약 프롬프트 적용.\n"
            "   - language: (선택 사항) 요약 결과 언어. 지정하지 않으면 영어(en)로 요약.\n\n"
            "       language code\n"
            "           - Korean: ko\n"
            "           - English: en\n\n"
            "**SummaryResponse**\n"
            "   - text: 요약된 텍스트."),
            response_model=SummaryResponse)
        async def summarize_gpt(
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
                    input_text=input_text,
                    language=request.language)
                # result = text_postprocess(result)
                # print(result)
                end = time.time()
                # ----------------------------------- #
                # print(f"Time: {end - st}")
            except AssertionError as e:
                self.server_logger.warn("error" + e)
                result += e
            except Exception as e:
                self.server_logger.warn("error" + e)
                result += "Error in summarize"
            finally:
                return SummaryResponse(text=result)

        @serve.batch(
            max_batch_size=4, 
            batch_wait_timeout_s=0.1)
        async def batched_generation(
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
