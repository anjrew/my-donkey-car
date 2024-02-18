FROM mcr.microsoft.com/vscode/devcontainers/base:ubuntu-20.04

# Install Miniconda
RUN wget https://repo.anaconda.com/miniconda/Miniconda3-py39_23.3.1-0-Linux-x86_64.sh && \
    bash Miniconda3-py39_23.3.1-0-Linux-x86_64.sh -b -p /miniconda && \
    rm Miniconda3-py39_23.3.1-0-Linux-x86_64.sh

# Add Miniconda to PATH
ENV PATH /miniconda/bin:$PATH

# Create Conda Environment and Install Dependencies
RUN conda create -n donkey python=3.9 -y && \
    conda run -n donkey pip install --default-timeout=120 --retries=5 donkeycar[pc]

# Clone Donkeycar Repository and Install in Developer Mode
WORKDIR /projects
RUN git clone https://github.com/autorope/donkeycar && \
    cd donkeycar && \
    git checkout main && \
    conda run -n donkey pip install -e .[pc]

# Install CUDA Toolkit
RUN conda install -n donkey cudatoolkit=11 -c pytorch -y

# Since `conda run` can have issues with interactive scripts, we use `/bin/bash -c` for commands needing the environment
# For commands that require the environment, use:
# RUN /bin/bash -c "source activate donkey && <your-command>"
# Example for creating a car directory (adjust if this command needs the environment):
RUN /bin/bash -c "source activate donkey && donkey createcar --path ~/mycar"

# Set the working directory to /projects/donkeycar
WORKDIR /projects/donkeycar

# Command to keep the container running (e.g., opening a shell)
CMD ["/bin/bash"]
