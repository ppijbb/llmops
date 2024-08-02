FROM public.ecr.aws/neuron/pytorch-inference-neuronx:2.1.2-neuronx-py310-sdk2.19.1-ubuntu20.04

# Install dependencies
RUN apt-get update && apt-get install -y \
    awscli \
    wget \
    unzip \
    git

# Install Neuron SDK
# RUN wget https://www.amazonaws.com/aws-neuron-docker/container/neuron_container-1.10.0.tar.gz && \
#     tar -xzf neuron_container-1.10.0.tar.gz && \
#     cd neuron_container-1.10.0 && \
#     ./build_and_install.sh

# Set environment variables
ENV NEURON_INSTALL_DIR=/opt/aws/neuron
ENV LD_LIBRARY_PATH=$NEURON_INSTALL_DIR/lib:$LD_LIBRARY_PATH
ENV PYTHONPATH=$NEURON_INSTALL_DIR/lib/python3.6/site-packages:$PYTHONPATH

# Install Python dependencies
COPY pyproject.toml pyproject.toml

RUN pip install -U pip
RUN pip install poetry
RUN poetry config virtualenvs.create false
RUN VLLM_TARGET_DEVICE=cpu poetry add optimum[neuronx]
RUN source /opt/aws_neuron_venv_pytorch/bin/activate

# Copy your code into the container
COPY . /app

# Set the working directory
WORKDIR /app

# Run your application
CMD ["python3", "deploy.py"]
