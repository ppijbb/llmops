FROM public.ecr.aws/neuron/pytorch-inference-neuronx:2.1.2-neuronx-py310-sdk2.19.1-ubuntu20.04

# Install dependencies
RUN apt-get update && apt-get install -y \
    awscli \
    wget \
    unzip

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
RUN pip3 install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-dev

# Copy your code into the container
COPY . .

# Set the working directory
WORKDIR /app

# Run your application
CMD ["python3", "deploy.py"]