## Environment Setup

The project can be set up in one of three ways, depending on your preference and the resources available to you:

### 1. Dev Container with VS Code

Using a development container within VS Code is recommended to maintain a consistent and isolated development environment. This approach leverages the Remote - Containers extension in VS Code to allow you to use a Docker container as a full-featured development environment. To set up a dev container in VS Code, follow these steps:

1. **Install Docker**: Ensure Docker is installed and running on your system. You can download it from [Docker's official website](https://www.docker.com/products/docker-desktop).

2. **Install the Remote - Containers Extension**: In VS Code, install the [Remote - Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) from the marketplace.

3. **Clone the Project Repository**: Use Git to clone the project repository to your local machine.

4. **Open the Project in VS Code**:
    - Open VS Code.
    - Go to `File > Open Folder` and select the root directory of the cloned project.

5. **Reopen in Container**:
    - With the project folder open, you'll see a popup in the bottom right corner suggesting to reopen the folder to develop in a container. Click `Reopen in Container`. If you don't see the popup, you can also open the Command Palette (`Ctrl+Shift+P` or `Cmd+Shift+P` on macOS) and select `Remote-Containers: Reopen in Container`.
    - VS Code will use the `Dockerfile` and `docker-compose.yml` in the `.devcontainer` directory of the project to build and start the container with all necessary dependencies installed.

6. **Develop Inside the Container**: Once the container is running, VS Code will attach to it. You can now use the VS Code terminal and editor to run commands and develop within the containerized environment. Any extensions or settings specified in the `.devcontainer` configuration will automatically be applied.

By following these steps, you can quickly set up a reproducible development environment tailored to the needs of the project, without needing to manually configure your local machine. This process ensures consistency across different machines and isolates your development environment from your local system setup.

### 2. Local Python Virtual Environment

Setting up a local Python virtual environment is straightforward and allows you to manage dependencies separately from your system's global Python environment. To set up a virtual environment:

- Ensure you have Python 3.9+ installed on your system.
- Navigate to the project's root directory in your terminal.
- Run `python3 -m venv venv` to create a new virtual environment in a folder named `venv`.
- Activate the virtual environment with `source venv/bin/activate` on Unix/macOS or `.\venv\Scripts\activate` on Windows.
- Install the required dependencies with `pip install -r requirements.txt`.

### 3. Conda Environment

A Conda environment is a great option if you prefer using Conda for managing packages and environments. To set up a Conda environment:

- Install Anaconda or Miniconda on your system.
- Create a new Conda environment by running `conda create --name donkeycar python=3.9`
- Activate the new environment with `conda activate donkeycar`.
- Navigate to the project's root directory and install the required dependencies with `pip install -r requirements.txt` or use `conda install` if you prefer installing packages directly through Conda.