# Note: You can use any Debian/Ubuntu based image you want. 
FROM mcr.microsoft.com/devcontainers/python:3.9-buster

# [Optional] Uncomment this section to install additional OS packages.
# RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
#     && apt-get -y install --no-install-recommends <your-package-list-here>

RUN pip install --upgrade pip

RUN pip install donkeycar[pc]

# Install Donkeycar (Developer Install for this example)
WORKDIR /projects
RUN git clone https://github.com/autorope/donkeycar && \
    cd donkeycar && \
    git checkout main && \
    pip install -e .[pc]

# Optional: Install CUDA toolkit for GPU support
RUN conda install cudatoolkit=11 -c pytorch

# Set the working directory to /projects/donkeycar
WORKDIR /projects/donkeycar

# Command to keep the container running (e.g., opening a shell)
CMD ["/bin/bash"]