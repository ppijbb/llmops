FROM public.ecr.aws/neuron/pytorch-inference-neuronx:2.1.2-neuronx-py310-sdk2.20.0-ubuntu20.04
# FROM public.ecr.aws/neuron/pytorch-training-neuronx:2.1.2-neuronx-py310-sdk2.19.1-ubuntu20.04

ARG HF_TOKEN
ARG VLLM_TARGET_DEVICE
ENV HF_TOKEN=${HF_TOKEN}
ENV VLLM_TARGET_DEVICE=${VLLM_TARGET_DEVICE}

# Set environment variables
ENV NEURON_INSTALL_DIR=/opt/aws/neuron
ENV LD_LIBRARY_PATH=$NEURON_INSTALL_DIR/lib:$LD_LIBRARY_PATH
ENV PYTHONPATH=$NEURON_INSTALL_DIR/lib/python3.10/site-packages:$PYTHONPATH
ENV PATH=/opt/aws/neuron/bin:$PATH
ENV NEURON_LIBRARY_PATH=/opt/aws/neuron/lib

# Install Python dependencies
COPY pyproject.toml pyproject.toml
COPY requirements.txt requirements.txt
COPY neuron_requirements.txt neuron_requirements.txt

# Update Neuron Compiler and Framework

ENV MAX_JOBS=4
ENV VLLM_BUILD_WITH_NEURON=true
RUN pip config set global.extra-index-url https://pip.repos.neuron.amazonaws.com && \
    pip install --upgrade -r requirements.txt  && \
    pip install --upgrade transformers git+https://github.com/huggingface/transformers.git && \
    pip install --pre --upgrade-strategy eager -r neuron_requirements.txt
RUN VLLM_TARGET_DEVICE="neuron" pip install 'vllm>=0.4.1,<0.5' &&\    
    pip install --upgrade-strategy eager torch==2.1.2 torchvision==0.16.2 torchaudio==2.1.2 torch-xla==2.1.2 triton==2.1.0 optimum-neuron git+https://github.com/huggingface/optimum-neuron.git

RUN pip cache purge
# Copy your code into the container

COPY . /app

# Set the working directory
WORKDIR /app

RUN huggingface-cli login --add-to-git-credential --token ${HF_TOKEN}

# Run your application
CMD ["gunicorn", "deploy:app", "--workers", "1", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]

