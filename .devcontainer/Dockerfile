# Use a specific version of the VS Code devcontainers base image
FROM mcr.microsoft.com/vscode/devcontainers/base:ubuntu-20.04

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

# Optional: Install CUDA toolkit in the 'donkey' environment if GPU support is needed
# RUN conda install -n donkey cudatoolkit=11 -c pytorch -y

# Ensure the 'vscode' user's shell is properly configured to use 'conda activate'
RUN echo ". /miniconda/etc/profile.d/conda.sh" >> /home/vscode/.bashrc && \
    echo "conda activate donkey" >> /home/vscode/.bashrc

# Set the working directory to the DonkeyCar project within the container
WORKDIR /projects/donkeycar

ENTRYPOINT ["/bin/bash", "-c", "sleep infinity"]
