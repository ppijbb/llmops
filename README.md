# Install Packages
```bash
pip install poetry
VLLM_TARGET_DEVICE=cpu poetry install
source ipex-llm-init -c --device cpu
``