# 기본 이미지 선택
FROM python:3.10-slim-bookworm as builder

# 빌드 시 필요한 인자 정의
ARG HF_TOKEN
ARG VLLM_TARGET_DEVICE
ENV HF_TOKEN=${HF_TOKEN} \
    VLLM_TARGET_DEVICE=${VLLM_TARGET_DEVICE} \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# 시스템 패키지 설치 및 캐시 정리
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git \
        build-essential && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 작업 디렉토리 설정
WORKDIR /app

# Python 패키지 설치
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -U https://github.com/Dao-AILab/flash-attention/releases/download/v2.6.3/flash_attn-2.6.3+cu118torch2.1cxx11abiFALSE-cp310-cp310-linux_x86_64.whl

# 런타임 스테이지
FROM python:3.10-slim-bookworm as runtime
ARG HF_TOKEN
ARG VLLM_TARGET_DEVICE

# 런타임에 필요한 환경변수 설정
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 

# 필요한 시스템 패키지만 설치
RUN apt-get update && \
    apt-get install -y --no-install-recommends git && \
    apt-get install build-essential -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# builder에서 설치된 Python 패키지 복사
COPY --from=builder /usr/local/lib/python3.10/site-packages/ /usr/local/lib/python3.10/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

WORKDIR /app
COPY . .

# 비root 사용자 생성 및 권한 설정
# RUN useradd -m -s /bin/bash appuser && \
#     chown -R appuser:appuser /app
# USER appuser

# Hugging Face 로그인
RUN huggingface-cli login --token ${HF_TOKEN} --add-to-git-credential
# 헬스체크 설정
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8507/health || exit 1

# 포트 설정
EXPOSE 8507
RUN echo $LD_LIBRARY_PATH
CMD ["serve", "run", "summary_serv:build_app"]
