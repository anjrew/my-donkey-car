# Use a specific version of the VS Code devcontainers base image
FROM mcr.microsoft.com/vscode/devcontainers/base:ubuntu-20.04

# Install system packages
RUN apt-get update && apt-get install -y --no-install-recommends \
        wget \
        git \
        libgl1-mesa-glx \
        libglib2.0-0

# Install Miniconda
RUN wget -q https://repo.anaconda.com/miniconda/Miniconda3-py39_23.3.1-0-Linux-x86_64.sh -O /tmp/miniconda.sh && \
    /bin/bash /tmp/miniconda.sh -b -p /miniconda && \
    rm /tmp/miniconda.sh

# Add Miniconda to PATH for all users
ENV PATH /miniconda/bin:$PATH

# Initialize Conda for bash shell and create the 'donkey' Conda environment
RUN conda init bash && \
    conda create -n donkey python=3.9 -y && \
    conda clean -afy

# Installing CUDA 10.0 and cuDNN 7.4, adjust TensorFlow version accordingly
RUN conda install -n donkey cudatoolkit=10.0 cudnn=7.4 -c conda-forge -y && \
    conda run -n donkey pip install tensorflow-gpu==2.2.0  # Example TensorFlow version, adjust as needed

# Install Donkeycar in the 'donkey' environment
RUN echo ". /miniconda/etc/profile.d/conda.sh" && \
    echo "conda activate donkey" && \
    conda run -n donkey pip install donkeycar[pc]

# Clone the DonkeyCar repository and install it in Developer Mode
WORKDIR /projects
RUN git clone https://github.com/autorope/donkeycar && \
    cd donkeycar && \
    git checkout main && \
    conda run -n donkey pip install -e .[pc]

# Ensure the 'vscode' user's shell is properly configured to use 'conda activate'
RUN echo ". /miniconda/etc/profile.d/conda.sh" >> /home/vscode/.bashrc && \
    echo "conda activate donkey" >> /home/vscode/.bashrc

# Set the working directory to the DonkeyCar project within the container
WORKDIR /projects/donkeycar

ENTRYPOINT ["/bin/bash", "-c", "sleep infinity"]
