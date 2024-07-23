# Install Packages

> 😒 python 버전은 3.10 고정 


tensorrt 가 현재(2024.07.23) 기준 python 3.11 버전 지원하지 않음

GPU를 사용하는 경우가 있을 수 있어 반드시 python 3.10 버전 사용할 것



```bash
pip install poetry
VLLM_TARGET_DEVICE=cpu poetry install
source ipex-llm-init -c --device cpu
```