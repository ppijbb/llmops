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

# Update Neuron Compiler and Framework

ENV MAX_JOBS=4
ENV VLLM_BUILD_WITH_NEURON=1
RUN pip config set global.extra-index-url https://pip.repos.neuron.amazonaws.com && \
    pip install -r requirements.txt --upgrade && \
    pip install --upgrade git+https://github.com/huggingface/transformers.git && \
    pip install \
        neuron \
        neuronx-cc==2.* \
        neuronx-cc-stubs \
        torch-neuronx >=2.1.2 \
        torchvision \
        transformers-neuronx >=0.12.0\
        libneuronxla \
        aws-neuronx-runtime-discovery \
        neuronx-distributed && \
    pip install --upgrade-strategy eager optimum[neuronx] &&\
    VLLM_TARGET_DEVICE="neuron" pip install torch-xla>=2.5.0 vllm triton>=3.*

RUN pip cache purge
# Copy your code into the container

COPY . /app

# Set the working directory
WORKDIR /app

RUN huggingface-cli login --add-to-git-credential --token ${HF_TOKEN}

# Run your application
CMD ["gunicorn", "deploy:app", "--workers", "1", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]

