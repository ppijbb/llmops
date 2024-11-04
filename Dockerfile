FROM python:3.10-slim

ARG HF_TOKEN
ARG VLLM_TARGET_DEVICE
ENV HF_TOKEN=${HF_TOKEN}
ENV VLLM_TARGET_DEVICE=${VLLM_TARGET_DEVICE}

COPY . /app
WORKDIR /app

# Set the working directory
RUN pip install poetry
RUN poetry lock && poetry install
RUN poetry run pip install flash-attn
RUN pip cache purge
RUN huggingface-cli login --add-to-git-credential --token ${HF_TOKEN}

CMD ["poetry", "run", "serve", "run", "summary_serv:build_app"]
