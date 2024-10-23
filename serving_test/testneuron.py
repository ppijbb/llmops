import subprocess
from typing import List, Dict
from ray import serve
from starlette.requests import Request
from fastapi import FastAPI
from argparse import ArgumentParser
import logging

logger = logging.getLogger("ray.serve")
app = FastAPI()


@serve.deployment(num_replicas=1, route_prefix="/")
@serve.ingress(app)
class BatchAPIIngress:
    def __init__(self, name="test", *args, **kwargs):
        self.name = name
        subprocess.run(["neuron-ls"])
  
    @serve.batch(max_batch_size=4)    
    def _classifier(self, input_text:List[str])->List[str]:
        return [{"label": str(i)} for i in range(len(input_text))]            

    @app.get("/")
    def batch(self, request:List[str])->List[str]:
        input_text = request.query_params["input_text"]
        return self._classifier(input_text)[0]["label"]

@serve.deployment
class BatchTextGenerator:
    def __init__(self, pipeline_key: str, model_key: str):
        self.model = (pipeline_key, model_key)

    @serve.batch(max_batch_size=4)
    async def handle_batch(self, inputs: List[str]) -> List[str]:
        print("Our input array has length:", len(inputs))

        results = self.model(inputs)
        return [result[0]["generated_text"] for result in results]

    async def __call__(self, request: Request) -> List[str]:
        return await self.handle_batch(request.query_params["text"])


def build_app(cli_args: Dict[str, str]) -> serve.Application:
    return BatchAPIIngress.options(
        placement_group_bundles=[{"CPU":1}], placement_group_strategy="STRICT_PACK"
    ).bind(
        BatchTextGenerator.bind("tesat", "any")
        )

# serve.run(BatchAPIIngress.bind(
#         BatchTextGenerator.bind("tesat", "any")
#         ))
