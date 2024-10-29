import os

os.environ["CUDA_VISIBLE_DEVICES"] = "0"
os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = "0"
os.environ["VLLM_CPU_KVCACHE_SPACE"] = "5"
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
import asyncio

from fastapi import FastAPI, Depends
from fastapi.responses import StreamingResponse
import logging
from typing import Any, List, Dict
import time
from summary.application import (LLMService, OpenAIService, llm_ready,
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


@serve.deployment(num_replicas=1, route_prefix="/")
@serve.ingress(app)
class APIIngress:
    def __init__(self, llm_handle: DeploymentHandle) -> None:
        self.service = llm_handle
 
    @serve.batch(
        max_batch_size=4, 
        batch_wait_timeout_s=0.1)
    async def batched_response(
        self, 
        data: List[Any]) -> List[str]:
        return await self.service.create_chat_completion.remote(data)
        
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
            input_text = text_preprocess(request.text)
            result += self.service.summarize.remote(
                input_prompt=request.prompt,
                input_text=input_text)
            # result = text_postprocess(result)
            # print(result)
            end = time.time()
            # ----------------------------------- #
            print(f"Time: {end - st}")
        except AssertionError as e:
            result += e
        except Exception as e:
            print(traceback(e))
            server_logger.error("error" + traceback(e))
            result += "Error in summarize"
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
        # service: OpenAIService = Depends(get_gpt_service)
        ) -> SummaryResponse:
        result = ""
        try:
            # ----------------------------------- #
            st = time.time()
            # result += ray.get(service.summarize.remote(ray.put(request.text)))
            # assert len(request.text ) > 200, "Text is too short"
            input_text = text_preprocess(request.text)
            result += await self.service.summarize.remote(
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

def build_app(cli_args: Dict[str, str]) -> serve.Application:
    return APIIngress.options(
        placement_group_bundles=[{"CPU":1., "GPU":1.}], 
        placement_group_strategy="STRICT_PACK"
    ).bind(
        LLMService.bind("test", "any")
        )