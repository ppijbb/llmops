FROM python:3.13.0b4-bookworm

# Install dependencies
RUN apt-get update && apt-get install -y \
    awscli \
    wget \
    unzip

# Install Neuron SDK
RUN wget https://www.amazonaws.com/aws-neuron-docker/container/neuron_container-1.10.0.tar.gz && \
    tar -xzf neuron_container-1.10.0.tar.gz && \
    cd neuron_container-1.10.0 && \
    ./build_and_install.sh

# Set environment variables
ENV NEURON_INSTALL_DIR=/opt/aws/neuron
ENV LD_LIBRARY_PATH=$NEURON_INSTALL_DIR/lib:$LD_LIBRARY_PATH
ENV PYTHONPATH=$NEURON_INSTALL_DIR/lib/python3.6/site-packages:$PYTHONPATH

# Install Python dependencies
COPY requirements.txt /app/requirements.txt
RUN pip3 install -r /app/requirements.txt

# Copy your code into the container
COPY . /app

# Set the working directory
WORKDIR /app

# Run your application
CMD ["python3", "your_script.py"]