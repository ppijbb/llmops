#     wget https://efa-installer.amazonaws.com/aws-efa-installer.key && gpg --import aws-efa-installer.key && \
# FROM 763104351884.dkr.ecr.us-east-1.amazonaws.com/huggingface-pytorch-inference-neuronx:2.1.2-neuronx-py310-sdk2.19.1-ubuntu20.04
FROM public.ecr.aws/neuron/pytorch-training-neuronx:2.1.2-neuronx-py310-sdk2.19.1-ubuntu20.04

ARG HF_TOKEN

ENV PATH=/opt/aws/neuron/bin:$PATH
# Set environment variables
ENV NEURON_INSTALL_DIR=/opt/aws/neuron
ENV LD_LIBRARY_PATH=$NEURON_INSTALL_DIR/lib:$LD_LIBRARY_PATH
ENV PYTHONPATH=$NEURON_INSTALL_DIR/lib/python3.6/site-packages:$PYTHONPATH
ENV HF_TOKEN=${HF_TOKEN}


# Install dependencies
RUN apt-get update -y && \
    apt-get upgrade -y && \
    apt-get install -y \
        awscli \
        wget \
        unzip \
        git

# RUN tee /etc/apt/sources.list.d/neuron.list > /dev/null <<EOF
# deb https://apt.repos.neuron.amazonaws.com ${VERSION_CODENAME} main
# EOF
# RUN curl -fsSL https://apt.repos.neuron.amazonaws.com/GPG-PUB-KEY-AMAZON-AWS-NEURON.PUB | apt-key add -
# RUN apt-get update -y && apt-get upgrade -y
# # RUN apt-get install linux-headers-$(uname -r) -y
# RUN apt-get install -y aws-neuronx-dkms=2.* \
#         aws-neuronx-collectives=2.* \
#         aws-neuronx-runtime-lib \
#         aws-neuronx-tools=2.*


# Install Neuron
RUN apt-get install aws-neuronx-dkms
RUN apt-get install aws-neuronx-runtime-lib
RUN apt-get install aws-neuronx-collectives

# Install EFA Driver (only required for multi-instance training)
RUN curl -O https://efa-installer.amazonaws.com/aws-efa-installer-latest.tar.gz && \
    wget https://efa-installer.amazonaws.com/aws-efa-installer.key && gpg --import aws-efa-installer.key && \
    cat aws-efa-installer.key | gpg --fingerprint && \
    wget https://efa-installer.amazonaws.com/aws-efa-installer-latest.tar.gz.sig && \
    gpg --verify ./aws-efa-installer-latest.tar.gz.sig && \
    tar -xvf aws-efa-installer-latest.tar.gz \
    cd aws-efa-installer && \
    sudo bash efa_installer.sh --yes &&\
    cd && \
    rm -rf aws-efa-installer-latest.tar.gz aws-efa-installer

# Install Python dependencies
COPY pyproject.toml pyproject.toml
RUN pip install poetry
RUN python -m pip config set global.extra-index-url https://pip.repos.neuron.amazonaws.com

# RUN poetry config virtualenvs.create false
RUN VLLM_TARGET_DEVICE=neuron poetry add git+https://github.com/huggingface/optimum-neuron.git
RUN poetry lock && poetry install --no-dev

# Update Neuron Compiler and Framework
RUN python -m pip install --upgrade neuronx-cc==2.* neuronx-cc-stubs torch-neuronx torchvision  transformers_neuronx
RUN python -m pip install optimum
RUN python -m pip install -U git+https://github.com/huggingface/optimum-neuron.git
RUN python -m pip install -U git+https://github.com/huggingface/transformers.git
# Copy your code into the container
COPY . /app

# Set the working directory
WORKDIR /app

RUN huggingface-cli login --add-to-git-credential --token ${HF_TOKEN}

# Run your application
CMD ["uvicorn", "deploy:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
