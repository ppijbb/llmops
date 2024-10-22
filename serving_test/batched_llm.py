# deployment.py
import ray
from ray import serve
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from vllm import LLM, SamplingParams
import asyncio
from collections import deque
import time
from bson.objectid import ObjectId


class ObjectId(ObjectId):
    pass
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    @classmethod
    def validate(cls, v):
        if not isinstance(v, ObjectId):
            raise TypeError('ObjectId required')
        return str(v)
    
# Pydantic 모델 정의
class GenerationRequest(BaseModel):
    prompt: str
    max_tokens: Optional[int] = 512
    temperature: Optional[float] = 0.7
    top_p: Optional[float] = 0.95
    request_id: ObjectId

class BatchRequest(BaseModel):
    requests: List[GenerationRequest]

class GenerationResponse(BaseModel):
    request_id: ObjectId
    generated_text: str
    processing_time: float

# Ray Serve 디플로이먼트 정의
@serve.deployment(
    ray_actor_options={"num_gpus": 1},
    max_concurrent_queries=10
)
class VLLMBatchDeployment:
    def __init__(self, model_name: str = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"):
        self.llm = LLM(
            model=model_name,
            trust_remote_code=True,
            tensor_parallel_size=1,  # GPU 수에 따라 조정
            max_num_batched_tokens=4096,
            gpu_memory_utilization=0.9
        )
        self.request_queue = deque()
        self.batch_size = 8
        self.max_batch_wait_time = 0.1  # 100ms

    async def process_batch(self):
        if not self.request_queue:
            return []

        batch_size = min(len(self.request_queue), self.batch_size)
        batch_requests = []
        start_times = []

        for _ in range(batch_size):
            request, start_time = self.request_queue.popleft()
            batch_requests.append(request)
            start_times.append(start_time)

        # vLLM 배치 처리를 위한 파라미터 준비
        prompts = [req.prompt for req in batch_requests]
        sampling_params = SamplingParams(
            temperature=batch_requests[0].temperature,
            top_p=batch_requests[0].top_p,
            max_tokens=batch_requests[0].max_tokens
        )

        # 배치 추론 실행
        outputs = self.llm.generate(prompts, sampling_params)
        
        # 결과 처리
        responses = []
        for i, output in enumerate(outputs):
            end_time = time.time()
            responses.append(GenerationResponse(
                request_id=batch_requests[i].request_id,
                generated_text=output.outputs[0].text,
                processing_time=end_time - start_times[i]
            ))

        return responses

    async def __process_batch_streaming(self, batch_requests, start_times):
        """스트리밍 방식으로 배치 처리를 수행하는 내부 메서드"""
        prompts = [req.prompt for req in batch_requests]
        sampling_params = SamplingParams(
            temperature=batch_requests[0].temperature,
            top_p=batch_requests[0].top_p,
            max_tokens=batch_requests[0].max_tokens
        )

        responses = []
        for i, output_generator in enumerate(self.llm.generate(prompts, sampling_params, use_tqdm=False)):
            generated_text = ""
            for output in output_generator:
                generated_text += output.outputs[0].text
            
            end_time = time.time()
            responses.append(GenerationResponse(
                request_id=batch_requests[i].request_id,
                generated_text=generated_text,
                processing_time=end_time - start_times[i]
            ))
        
        return responses

    async def handle_request(self, request: GenerationRequest):
        start_time = time.time()
        self.request_queue.append((request, start_time))

        # 배치 크기에 도달하거나 최대 대기 시간이 경과할 때까지 대기
        if len(self.request_queue) >= self.batch_size:
            responses = await self.process_batch()
        else:
            await asyncio.sleep(self.max_batch_wait_time)
            responses = await self.process_batch()

        # 현재 요청에 해당하는 응답 찾기
        for response in responses:
            if response.request_id == request.request_id:
                return response

        raise HTTPException(status_code=500, detail="Request processing failed")

    async def handle_batch_request(self, batch_request: BatchRequest):
        tasks = []
        for request in batch_request.requests:
            tasks.append(self.handle_request(request))
        
        try:
            responses = await asyncio.gather(*tasks)
            return responses
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Batch processing failed: {str(e)}")

# FastAPI 앱 설정
app = FastAPI()

@serve.deployment(route_prefix="/")
@serve.ingress(app)
class FastAPIDeployment:
    def __init__(self, vllm_handle):
        self.vllm_handle = vllm_handle

    @app.post("/generate")
    async def generate(self, request: GenerationRequest):
        try:
            return await self.vllm_handle.handle_request.remote(request)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/batch_generate")
    async def batch_generate(self, batch_request: BatchRequest):
        try:
            return await self.vllm_handle.handle_batch_request.remote(batch_request)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/health")
    async def health_check():
        return {"status": "healthy"}

# 서버 구동 코드
if __name__ == "__main__":
    ray.init()
    serve.run(FastAPIDeployment.bind(VLLMBatchDeployment.bind()))
