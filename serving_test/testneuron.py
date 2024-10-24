import subprocess
from typing import List, Dict
from datetime import datetime
from ray import serve
from ray.serve.handle import DeploymentHandle
from starlette.requests import Request
from fastapi import FastAPI
from pydantic import BaseModel
import logging

logger = logging.getLogger("ray.serve")
app = FastAPI()

class GenerationRequest(BaseModel):
    input_text: str


@serve.deployment(num_replicas=3, route_prefix="/")
@serve.ingress(app)
class BatchAPIIngress:
    def __init__(self, batch_handler: DeploymentHandle, *args, **kwargs):
        self.handle = batch_handler
        
        try:
            subprocess.run(["neuron-ls"])
            logger.info("Yes Neuron")
        except:
            logger.warning("No Neuron")
            
    @serve.batch(max_batch_size=8, batch_wait_timeout_s=0.3)
    async def _classifier(self, input_text:List[str])->List[str]:
        return await self.handle.handle_batch.remote(input_text)

    @app.post("/")
    async def batch(self, requests: GenerationRequest)->str:
        return await self._classifier(requests.input_text)

@serve.deployment
class BatchTextGenerator:
    def __init__(self, pipeline_key: str, model_key: str):
        self.parsed = (pipeline_key, model_key)
        
    async def model(self, inputs: List[str]):
        return [{"generated_text": f"Hello {datetime.now().strftime('%Y%m%d %H:%M:%S')}"} for i in range(len(inputs))]

    async def handle_batch(self, inputs: List[str]) -> List[str]:
        print("Our input array has length:", len(inputs))
        print("Our input array has length:", inputs)
        results = await self.model(inputs)
        results = [result["generated_text"] for result in results]
        print(results)
        return results

    # async def __call__(self, input_texts: List[GenerationRequest]) -> List[str]:
    #     return await self.handle_batch([x.input_text for x in input_texts])

def build_app(cli_args: Dict[str, str]) -> serve.Application:
    return BatchAPIIngress.options(
        placement_group_bundles=[{"CPU":1}], 
        placement_group_strategy="STRICT_PACK"
    ).bind(
        BatchTextGenerator.bind("test", "any")
        )

# serve.run(BatchAPIIngress.bind(
#         BatchTextGenerator.bind("test", "any")
#         ))
