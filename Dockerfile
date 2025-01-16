FROM python:3.10-bookworm as builder

ARG HF_TOKEN
ARG VLLM_TARGET_DEVICE
ENV HF_TOKEN=${HF_TOKEN}
ENV VLLM_TARGET_DEVICE=${VLLM_TARGET_DEVICE}

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y git

WORKDIR /app
COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install -U https://github.com/Dao-AILab/flash-attention/releases/download/v2.6.3/flash_attn-2.6.3+cu118torch2.1cxx11abiFALSE-cp310-cp310-linux_x86_64.whl && \
    pip cache purge

FROM builder as runtime

COPY . /app
WORKDIR /app

RUN huggingface-cli login --add-to-git-credential --token ${HF_TOKEN}

CMD ["serve", "run", "summary_serv:build_app"]
