#     wget https://efa-installer.amazonaws.com/aws-efa-installer.key && gpg --import aws-efa-installer.key && \
# FROM 763104351884.dkr.ecr.us-east-1.amazonaws.com/huggingface-pytorch-inference-neuronx:2.1.2-neuronx-py310-sdk2.19.1-ubuntu20.04
FROM public.ecr.aws/neuron/pytorch-training-neuronx:2.1.2-neuronx-py310-sdk2.19.1-ubuntu20.04

ARG HF_TOKEN
ENV HF_TOKEN=${HF_TOKEN}

# Set environment variables
ENV NEURON_INSTALL_DIR=/opt/aws/neuron
ENV LD_LIBRARY_PATH=$NEURON_INSTALL_DIR/lib:$LD_LIBRARY_PATH
ENV PYTHONPATH=$NEURON_INSTALL_DIR/lib/python3.10/site-packages:$PYTHONPATH
ENV PATH=/opt/aws/neuron/bin:$PATH
ENV NEURON_LIBRARY_PATH=/opt/aws/neuron/lib

# Install Python dependencies
COPY pyproject.toml pyproject.toml
COPY requirements.txt requirements.txt

# RUN poetry config virtualenvs.create false
# RUN pip install poetry
# RUN poetry lock
# RUN poetry add git+https://github.com/huggingface/optimum-neuron.git
# RUN poetry install
# RUN poetry env remove python
        
# Update Neuron Compiler and Framework

ENV VLLM_TARGET_DEVICE=neuron
ENV MAX_JOBS=4
ENV VLLM_BUILD_WITH_NEURON=1
RUN pip config set global.extra-index-url https://pip.repos.neuron.amazonaws.com && \
    pip install -r requirements.txt --upgrade && \
    pip install --upgrade neuron neuronx-cc==2.* neuronx-cc-stubs torch-neuronx torchvision \
                        transformers_neuronx libneuronxla aws-neuronx-runtime-discovery neuronx-distributed && \
    pip install --upgrade-strategy eager optimum[neuronx] && \
    pip install --upgrade git+https://github.com/huggingface/transformers.git
# Copy your code into the container

COPY . /app

# Set the working directory
WORKDIR /app

RUN huggingface-cli login --add-to-git-credential --token ${HF_TOKEN}
# RUN gunicorn --help
# RUN  serve run serve:build_app\
#     model=TinyLlama/TinyLlama-1.1B-Chat-v1.0\
#     device=neruon\
#     dtype=bfloat16\
#     gpu_memory_utilization=.95\
#     max_model_len=127
# Run your application
CMD ["gunicorn", "deploy:app", "--workers", "1", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]

