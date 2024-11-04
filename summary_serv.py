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


def text_preprocess(text: str) -> str:
    return text
    # return f"[대화]\n{text}\n---\n[요약]\n" if "[대화]" not in text and "[요약]" not in text else text

def text_postprocess(text:str) -> str:
    if not text.endswith("\n---"):
        text = "* " + "* ".join(text.split("* ")[:-1])
        if text.endswith("\n---"):
            "---"
    return text.replace("* ", "").replace("---", "").strip()


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
            print(traceback(e))
            server_logger.error("error" + traceback(e))
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
            print(traceback(e))
            server_logger.error("error" + traceback(e))
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
            server_logger.warn("error" + traceback(e))
            result += e
        except Exception as e:
            server_logger.warn("error" + traceback(e))
            result += "Error in summarize"
        finally:
            return SummaryResponse(text=result)

    @serve.batch(
        max_batch_size=4, 
        batch_wait_timeout_s=0.1)
    async def batched_transcript(
        self, 
        request_prompt: List[Any],
        request_text: List[Any]
    ) -> List[str]:
        logger.info(f"Batched request: {len(request_text)}")
        return await self.service.transcript.remote(
            input_prompt=request_prompt,
            input_text=request_text,
            batch=True)

    @app.post(
        "/transcript_gemma", 
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
            print(traceback(e))
            server_logger.error("error" + traceback(e))
            result += "Generation failed"
        finally:
            return SummaryResponse(text=result)

    @app.post(
        "/transcript", 
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
            result += await service.transcript(
                input_prompt=request.prompt,
                input_text=input_text)
            # result = text_postprocess(result)
            # print(result)
            end = time.time()
            # ----------------------------------- #
            # print(f"Time: {end - st}")
        except AssertionError as e:
            server_logger.warn("error" + traceback(e))
            result += e
        except Exception as e:
            server_logger.warn("error" + traceback(e))
            result += "Error in summarize"
        finally:
            return SummaryResponse(text=result)

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
            print(traceback(e))
            server_logger.error("error" + traceback(e))
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
            server_logger.warn("error" + traceback(e))
            result += e
        except Exception as e:
            server_logger.warn("error" + traceback(e))
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

serve.start(http_options={"host":"0.0.0.0", "port": 8501})
