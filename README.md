# Setup Environment

> 😒 python 버전은 3.10 고정 

## CPU, GPU

tensorrt 가 현재(2024.07.23) 기준 python 3.11 버전 지원하지 않음

GPU를 사용하는 경우가 있을 수 있어 반드시 python 3.10 버전 사용할 것

## AWS Inferentia

inf1.xlarge 인스턴스 기준으로만 생각하는 편이 제일 저렴
-> inferentia2 부터 transformers decoder 지원

## 필수 Environment Variables
```bash
OPENAI_API_KEY <= 슬랙 통하여 직접 전달 받기
HF_TOKEN <= 허깅페이스 계정으로 발급 필요(write token)
```

## Installation in CPU

```bash
pip install poetry
VLLM_TARGET_DEVICE=cpu poetry install
source ipex-llm-init -c --device cpu
```

## Installation in GPU
```bash
pip install -r requirements.txt
```

## Installation in CPU
```bash
pip install poetry

poetry lock && poetry install
```

## Installation in Inferentia
```bash
# docker compose build(Recommended)
docker compose -f ./inferentia/docker-compose.yaml build
# docker build
docker build --tag {tag} ./inferentia
```
# Run Server

## Run Server with GPU
```bash
# Build server with docker image
docker compose build
# Run server with container
docker compose up
# witout Docker, 
serve run summary_serv:build_app
```

## Run Server with CPU
```bash
# Build server with docker image
docker compose build
# Run server with container
docker compose up
# witout Docker, 
serve run summary_serv:build_app
```

## Run Server with Inferentia
```bash
# docker compose build(Recommended)
docker compose -f ./inferentia/docker-compose.yaml up
```
