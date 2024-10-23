import os
from typing import Dict, Optional, List, Any
import logging
from argparse import ArgumentParser as Parser
from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import StreamingResponse, JSONResponse
import subprocess
from ray import serve

from vllm.engine.arg_utils import AsyncEngineArgs, EngineArgs
from vllm.engine.llm_engine import LLMEngine
from vllm.engine.async_llm_engine import AsyncLLMEngine
from vllm.entrypoints.openai.cli_args import make_arg_parser
from vllm.entrypoints.openai.protocol import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    ErrorResponse,
)
from vllm.entrypoints.openai.serving_chat import OpenAIServingChat
# from vllm.entrypoints.openai.serving_engine import LoRAModulePath, PromptAdapterPath
# from vllm.utils import FlexibleArgumentParser
# from vllm.entrypoints.logger import RequestLogger


os.environ['NEURON_VISIBLE_CORES']='2'
os.environ['NEURON_RT_NUM_CORES']='2'
os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = "0"
os.environ["VLLM_CPU_KVCACHE_SPACE"] = "2"
os.environ["VLLM_CPU_OMP_THREADS_BIND"] = "0-29"
os.environ["RAY_DEDUP_LOGS"] = "0" 
# os.environ["VLLM_ATTENTION_BACKEND"] = "XFORMERS"

# creates XLA hlo graphs for all the context length buckets.
os.environ['NEURON_CONTEXT_LENGTH_BUCKETS'] = "128,512,1024,2048"
# creates XLA hlo graphs for all the token gen buckets.
os.environ['NEURON_TOKEN_GEN_BUCKETS'] = "128,512,1024,2048"


logger = logging.getLogger("ray.serve")

app = FastAPI()

@serve.deployment
class BatchTextGenerator:
    def __init__(self, pipeline_key: str, model_key: str):
        self.model = pipeline(pipeline_key, model_key)

    @serve.batch(max_batch_size=4)
    async def handle_batch(self, inputs: List[str]) -> List[str]:
        print("Our input array has length:", len(inputs))

        results = self.model(inputs)
        return [result[0]["generated_text"] for result in results]

    async def __call__(self, request: Request) -> List[str]:
        return await self.handle_batch(request.query_params["text"])


@serve.deployment(num_replicas=1, route_prefix="/")
@serve.ingress(app)
class APIIngress:
    def __init__(self, vllm_model_handle) -> None:
        self.handle = vllm_model_handle
    
    @serve.batch(max_batch_size=4, batch_wait_timeout_s=0.1)
    @app.get("/")
    async def handle_batch(self, inputs: List[str]) -> List[str]:
        print("Our input array has length:", len(inputs))
        results = await self.genrate(inputs)
        return [result[0]["generated_text"] for result in results]
    
    async def generate(self, prompt: List[str]) -> List[str]:
        return await self.handle.create_chat_completion.remote(prompt)


@serve.deployment(
    autoscaling_config={
        "min_replicas": 1,
        "max_replicas": 2,
        "target_ongoing_requests": 5,
    },
    ray_actor_options={
        "resources": {
            "neuron_cores": 2
            },
        "runtime_env": {
            "env_vars": {
                "NEURON_CC_FLAGS": "-O1"
                }
            },
        },
    max_ongoing_requests=10)
class VLLMDeployment:
    def __init__(
        self,
        engine_args: EngineArgs | AsyncEngineArgs,
        response_role: str,
        lora_modules: Optional[List[Any]]= None, # Optional[List[LoRAModulePath]] = None,
        chat_template: Optional[str] = None,
    ):
        logger.info(f"Starting with engine args: {engine_args}")
        self.openai_serving_chat = None
        self.engine_args = engine_args
        self.response_role = response_role
        # self.lora_modules = lora_modules
        self.chat_template = chat_template
        self.engine = LLMEngine.from_engine_args(engine_args)
        
        print("VLLMDeployment initialized")
        # try:
        #     self.engine = AsyncLLMEngine.from_engine_args(engine_args)
        # except NotImplementedError:
        #     self.engine = LLMEngine.from_engine_args(engine_args)
        # except Exception as e:
        #     logger.error(f"Failed to create engine: {e}")
        #     raise e

    # @app.post("/summarize")
    async def create_chat_completion(
        self, 
        request: ChatCompletionRequest, 
        raw_request: Request
    ):
        """OpenAI-compatible HTTP endpoint.

        API reference:
            - https://docs.vllm.ai/en/latest/serving/openai_compatible_server.html
        """
        if not self.openai_serving_chat:
            model_config = self.engine.get_model_config()
            # Determine the name of the served model for the OpenAI client.
            if self.engine_args.served_model_name is not None:
                served_model_names = self.engine_args.served_model_name
            else:
                served_model_names = [self.engine_args.model]
            self.openai_serving_chat = OpenAIServingChat(
                self.engine,
                model_config,
                served_model_names,
                self.response_role,
                self.lora_modules,
                self.chat_template,
            )
        logger.info(f"Request: {request}")
        generator = self.openai_serving_chat.create_chat_completion(
            request, raw_request
        )
        if isinstance(generator, ErrorResponse):
            return JSONResponse(
                content=generator.model_dump(), status_code=generator.code
            )
        if request.stream:
            return StreamingResponse(content=generator, media_type="text/event-stream")
        else:
            assert isinstance(generator, ChatCompletionResponse)
            return JSONResponse(content=generator.model_dump())


def parse_vllm_args(cli_args: Dict[str, str]):
    """Parses vLLM args based on CLI inputs.

    Currently uses argparse because vLLM doesn't expose Python models for all of the
    config options we want to support.
    """
    # arg_parser = EngineArgs.add_cli_args(Parser())
        # description="vLLM OpenAI-Compatible RESTful API server."

    parser = make_arg_parser(
        # arg_parser
        )
    arg_strings = [ # defualt arguments
        "--model", "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
        "--device", "neuron",
        "--dtype", "float16",
        "--gpu-memory-utilization", "0.95",
        "--max-model-len", "1024",
        "--max-num-seqs", "8",
        "--tensor-parallel-size", "2",
        ]
    for key, value in cli_args.items():
        arg_strings.extend([f"--{key}", str(value)])
    logger.info(arg_strings)
    parsed_args = parser.parse_args(args=arg_strings)
    return parsed_args


def build_app(cli_args: Dict[str, str]) -> serve.Application:
    """Builds the Serve app based on CLI arguments.

    See https://docs.vllm.ai/en/latest/serving/openai_compatible_server.html#command-line-arguments-for-the-server
    for the complete set of arguments.

    Supported engine arguments: https://docs.vllm.ai/en/latest/models/engine_args.html.
    """  # noqa: E501
    parsed_args = parse_vllm_args(cli_args)
    # engine_args = AsyncEngineArgs.from_cli_args(parsed_args)
    engine_args = EngineArgs.from_cli_args(parsed_args) # neuron is not supported for async yet
    engine_args.worker_use_ray = True

    tp = engine_args.tensor_parallel_size
    logger.info(f"Tensor parallelism = {tp}")
    pg_resources = []
    pg_resources.append({"CPU": 1, "neuron_cores":2})  # for the deployment replica
    for i in range(tp):
        pg_resources.append({
            "CPU": 1,#, "GPU": 1
        })  # for the vLLM actors
    # We use the "STRICT_PACK" strategy below to ensure all vLLM actors are placed on
    # the same Ray node.
    return APIIngress.bind(
        VLLMDeployment
        .options(
            placement_group_bundles=pg_resources,  
            placement_group_strategy="STRICT_PACK")
        .bind(
            engine_args,
            parsed_args.response_role,
            parsed_args.lora_modules,
            parsed_args.chat_template)
        )

