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

from fastapi import FastAPI, Depends
from fastapi.responses import StreamingResponse
import logging
from typing import Annotated
import time
from summary.application import (LLMService, OpenAIService, 
                                 get_llm_service, get_gpt_service)
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

def text_preprocess(text: str) -> str:
    return text
    # return f"[대화]\n{text}\n---\n[요약]\n" if "[대화]" not in text and "[요약]" not in text else text

def text_postprocess(text:str) -> str:
    if not text.endswith("\n---"):
        text = "* " + "* ".join(text.split("* ")[:-1])
        if text.endswith("\n---"):
            "---"
    return text.replace("* ", "").replace("---", "").strip()


@app.post("/summarize_llama", 
          response_model=SummaryResponse)
async def summarize(
    request: SummaryRequest,
    service: LLMService = Depends(get_llm_service)) -> SummaryResponse:
    result = ""
    # Generate predicted tokens
    try:
        # ----------------------------------- #
        st = time.time()
        # result += ray.get(service.summarize.remote(ray.put(request.text)))
        # assert len(request.text ) > 200, "Text is too short"
        input_text = text_preprocess(request.text)
        result += service.summarize(
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
        logging.error("error" + traceback(e))
        result += "Error in summarize"
    finally:
        return SummaryResponse(text=result)


@app.post("/summarize_stream",)
async def summarize_stream(
    request: SummaryRequest,
    service: LLMService = Depends(get_llm_service)):
    result = ""
    # Generate predicted tokens
    try:
        # ----------------------------------- #
        st = time.time()
        # result += ray.get(service.summarize.remote(ray.put(request.text)))
        # assert len(request.text ) > 200, "Text is too short"
        return StreamingResponse(
            content=service.summarize(
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
        logging.error("error" + traceback(e))
        result += "Error in summarize"


@app.post("/summarize", 
          response_model=SummaryResponse)
async def summarize_gpt(
    request: SummaryRequest,
    service: OpenAIService = Depends(get_gpt_service)) -> SummaryResponse:
    result = ""
    await service.summarize(
            input_prompt=request.prompt,
            input_text=request.text)
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
        print(f"Time: {end - st}")
    except AssertionError as e:
        result += e
    except Exception as e:
        print(traceback(e))
        logging.error("error" + traceback(e))
        result += "Error in summarize"
    finally:
        return SummaryResponse(text=result)
