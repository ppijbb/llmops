FROM public.ecr.aws/neuron/pytorch-inference-neuronx:2.1.2-neuronx-py310-sdk2.19.1-ubuntu20.04

# Install dependencies
RUN apt-get update && apt-get install -y \
    awscli \
    wget \
    unzip \
    git


# Set environment variables
ENV NEURON_INSTALL_DIR=/opt/aws/neuron
ENV LD_LIBRARY_PATH=$NEURON_INSTALL_DIR/lib:$LD_LIBRARY_PATH
ENV PYTHONPATH=$NEURON_INSTALL_DIR/lib/python3.6/site-packages:$PYTHONPATH

# Install Neuron SDK
# RUN wget https://www.amazonaws.com/aws-neuron-docker/container/neuron_container-1.10.0.tar.gz && \
#     tar -xzf neuron_container-1.10.0.tar.gz && \
#     cd neuron_container-1.10.0 && \
#     ./build_and_install.sh

# Install Python dependencies
COPY pyproject.toml pyproject.toml

RUN pip install -U pip
RUN pip install poetry
RUN poetry config virtualenvs.create false
RUN VLLM_TARGET_DEVICE=cpu poetry add git+https://github.com/ppijbb/optimum-neuron.git
RUN poetry lock && poetry install --no-dev
# RUN source /opt/aws_neuron_venv_pytorch/bin/activate

# Copy your code into the container
COPY . /app

# Set the working directory
WORKDIR /app

RUN huggingface-cli login --add-to-git-credential --token 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

# Run your application
CMD ["uvicorn", "deploy:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
