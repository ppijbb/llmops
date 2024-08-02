import os

os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = "0"
# os.environ["VLLM_CPU_KVCACHE_SPACE"] = "40"
# os.environ["VLLM_CPU_OMP_THREADS_BIND"] = "0-29"
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

from fastapi import FastAPI, Depends
from fastapi.responses import StreamingResponse
import logging
from typing import Annotated
import time
from summary.depend import get_model
from summary.application import LLMService, get_llm_service
from summary.dto import SummaryRequest, SummaryResponse
import traceback
import os
import ray
import torch


def format_llm_output(rlt_text):
    return {
        'text': rlt_text
    }

app = FastAPI(title="dialog summary")

logging.info("Server Running...")

@app.post("/summarize", response_model=SummaryResponse)
async def summarize(request: SummaryRequest,
                    service: LLMService = Depends(get_llm_service)) -> SummaryResponse:
    result = ""
    # Generate predicted tokens
    try:
        # ----------------------------------- #
        # st = time.time()
        # result += ray.get(service.summarize.remote(ray.put(request.text)))
        result += service.summarize(request.text)
        print(result)
        # end = time.time()
        # ----------------------------------- #

    except Exception as e:
        print(traceback(e))
        logging.error("error" + traceback(e))
        result += "Error in summarize"
    finally:
        return SummaryResponse(text=result)


@app.post("/summarize_stream",)
async def summarize(request: SummaryRequest,
                    service: LLMService = Depends(get_llm_service)):
    result = ""
    # Generate predicted tokens
    try:
        # ----------------------------------- #
        # st = time.time()
        # result += ray.get(service.summarize.remote(ray.put(request.text)))
        return StreamingResponse(
            content=service.summarize(request.text, stream=True),
            media_type="text/event-stream")
        # end = time.time()
        # ----------------------------------- #

    except Exception as e:
        print(traceback(e))
        logging.error("error" + traceback(e))
        result += "Error in summarize"
    
    # finally:
    #     return SummaryResponse(text=result)
