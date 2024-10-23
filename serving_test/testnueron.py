import subprocess


print(subprocess.run(["neuron-ls"], capture_output=True, check=True))


import subprocess
from typing import List, Dict
from ray import serve
from fastapi import FastAPI
from argparse import ArgumentParser

app = FastAPI()


@serve.deployment
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
    
    
def build_app(cli_args: Dict[str, str], *args, **kwargs) -> serve.Application:
    parser = ArgumentParser()
    return BatchAPIIngress.bind(*args, **kwargs)
