import os

os.environ["CUDA_VISIBLE_DEVICES"] = "0"
os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = "0"
os.environ["VLLM_CPU_KVCACHE_SPACE"] = "2"
os.environ["VLLM_CPU_OMP_THREADS_BIND"] = "0-29"
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
import torch

from fastapi import FastAPI, Depends
from fastapi.responses import StreamingResponse
import logging
from typing import Any, List, Dict
import time
from summary.application.engine import (
    LLMService, OpenAIService, llm_ready,
    get_llm_service, get_gpt_service)
from summary.dto import SummaryRequest, SummaryResponse
from summary.dto import TranscriptRequest, TranscriptResponse
from summary.utils.text_process import text_preprocess, text_postprocess
from summary.logger import setup_logger
import traceback
import os
from ray import serve
from ray.serve.handle import DeploymentHandle


def format_llm_output(rlt_text):
    return {
        'text': rlt_text
    }

app = FastAPI(
    title="dialog summary",
    lifespan=llm_ready,
    )
logger = logging.getLogger("ray.serve")
server_logger = setup_logger()
server_logger.info("""
####################
#  Server Started  #
####################
""")


@serve.deployment(num_replicas=1)
@serve.ingress(app=app)
class APIIngress:
    def __init__(self, llm_handle: DeploymentHandle) -> None:
        self.service = llm_handle
 
    @serve.batch(
        max_batch_size=4, 
        batch_wait_timeout_s=0.1)
    async def batched_summary(
        self, 
        request_prompt: List[Any],
        request_text: List[Any]
    ) -> List[str]:
        logger.info(f"Batched request: {len(request_text)}")
        return await self.service.summarize.remote(
            input_prompt=request_prompt,
            input_text=request_text,
            batch=True)
        
    @app.post(
        "/summarize_llama", 
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
            server_logger.error("error" + e)
            result += "Generation failed"
        finally:
            return SummaryResponse(text=result)

    @app.post(
        "/summarize_stream",
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
            server_logger.error("error" + e)
            result += "Error in summarize"


    @app.post(
        "/summarize", 
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
            server_logger.warn("error" + e)
            result += e
        except Exception as e:
            server_logger.warn("error" + e)
            result += "Error in summarize"
        finally:
            return SummaryResponse(text=result)

    @serve.batch(
        max_batch_size=4, 
        batch_wait_timeout_s=0.1)
    async def batched_transcript(
        self, 
        request_prompt: List[Any],
        request_text: List[Any],
        source_language: str,
        target_language: str
    ) -> List[str]:
        logger.info(f"Batched request: {len(request_text)}")
        return await self.service.transcript.remote(
            input_prompt=request_prompt,
            input_text=request_text,
            soruce_lang=source_language,
            target_lang=str(request.target_language),
            batch=True)

    @app.post(
        "/transcript_gemma", 
        description='''
        language code
        - Korean: ko
        - English: en
        - Chinese: zh
        - French: fr
        - Spanish: es
        ''',
        response_model=TranscriptResponse)
    async def transcript(
        self,
        request: TranscriptRequest,
        # service: LLMService = Depends(get_llm_service)
    ) -> TranscriptResponse:
        result = ""
        # Generate predicted tokens
        try:
            # ----------------------------------- #
            st = time.time()
            # result += ray.get(service.summarize.remote(ray.put(request.text)))
            # assert len(request.text ) > 200, "Text is too short"
            result += await self.batched_transcript(
                request_prompt=None,
                soruce_lang=request.source_language,
                target_lang=str(request.target_language),
                request_text=f'source text: {text_preprocess(request.text)}')
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
            server_logger.error("error" + e)
            result += "Generation failed"
        finally:
            return TranscriptResponse(text=result)

    @app.post(
        "/transcript",
        description='''
        language code
        - Korean: ko
        - English: en
        - Chinese: zh
        - French: fr
        - Spanish: es
        ''',
        response_model=TranscriptResponse)
    async def transcript_gpt(
        self,
        request: TranscriptRequest,
        service: OpenAIService = Depends(get_gpt_service)
    ) -> TranscriptResponse:
        result = ""
        print("source", request.source_language)
        print("target", request.target_language)
        try:
            # ----------------------------------- #
            st = time.time()
            # result += ray.get(service.summarize.remote(ray.put(request.text)))
            # assert len(request.text ) > 200, "Text is too short"
            input_text = text_preprocess(request.text)
            result += await service.transcript(
                input_prompt=None,
                soruce_lang=request.source_language,
                target_lang=request.target_language,
                input_text=input_text)
            # result = text_postprocess(result)
            # print(result)
            end = time.time()
            # ----------------------------------- #
            print(f"Time: {end - st}")
        except AssertionError as e:
            server_logger.warn("error" + e)
            result += e
        except Exception as e:
            server_logger.warn("error" + e)
            result += "Error in summarize"
        finally:
            return TranscriptResponse(text=result)

    @app.post(
        "/transcript_gemma/summarize", 
        response_model=SummaryResponse)
    async def transcript(
        self,
        request: SummaryRequest,
        # service: LLMService = Depends(get_llm_service)
    ) -> SummaryResponse:
        result = ""
        # Generate predicted tokens
        result += await self.batched_transcript(
                request_prompt=request.prompt,
                request_text=text_preprocess(request.text))
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
            server_logger.error("error" + e)
            result += "Generation failed"
        finally:
            return SummaryResponse(text=result)

    @app.post(
        "/transcript/summarize", 
        response_model=SummaryResponse)
    async def transcript_gpt(
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
            result += await service.transcript_summarize(
                input_prompt=request.prompt,
                input_text=input_text)
            # result = text_postprocess(result)
            # print(result)
            end = time.time()
            # ----------------------------------- #
            # print(f"Time: {end - st}")
        except AssertionError as e:
            server_logger.warn("error" + e)
            result += e
        except Exception as e:
            server_logger.warn("error" + e)
            result += "Error in summarize"
        finally:
            return SummaryResponse(text=result)

def build_app(
    cli_args: Dict[str, str]
) -> serve.Application:
    return APIIngress.options(
        placement_group_bundles=[{"CPU":1.0, "GPU": 0.4}], 
        placement_group_strategy="STRICT_PACK",
        ).bind(
            LLMService.bind()
            )

serve.start(http_options={"host": "0.0.0.0", "port": 8501})
