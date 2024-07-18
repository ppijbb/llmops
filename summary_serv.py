from fastapi import FastAPI, Depends
import logging
from typing import Annotated
import time
from summary.depend import get_model
from summary.application import LLMService, get_llm_service
from summary.dto import SummaryRequest, SummaryResponse
import traceback
import os
import ray
os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'


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
        st = time.time()
        text = ray.put(request.text)
        result += ray.get(service.summarize.remote(text))
        end = time.time()
        # ----------------------------------- #

        # logging.warn(f'Inference time: {end-st} s')
        # logging.warn(('-'*20) + 'Prompt' + ('-'*20))
        # logging.warn(input_text)
        # logging.warn(('-'*20) + 'Output (skip_special_tokens=False)' + ('-'*20))
        # logging.warn(output_str)

    except Exception as e:
        print(traceback(e))
        result += "Error in summarize"
    finally:
        return SummaryResponse(text=result)

