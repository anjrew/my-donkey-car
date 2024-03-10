# Train container

The train container is a Docker container that contains all the necessary dependencies to train a model. The container is based on the official TensorFlow Docker image. The container is available on Docker Hub.

By default donkey uses tensorflow version 2.10.0 so we use the same version in the container.

```bash
docker pull tensorflow/tensorflow:2.10.1-gpu
```

To build the Docker image with Donkeycar installed, follow these steps:


1. Open a terminal or command prompt, navigate to the project root directory, and run the following command to build the Docker image:
```bash
docker build -t donkeycar-model-trainer -f docker/Training.Dockerfile docker/ 
```

This command will build the Docker image based on the instructions in the Dockerfile and tag it as donkeycar-model-trainer. You can choose a different tag name if desired.

2. Once the image is built, you can run the Docker container using the following command:

```bash
docker run --gpus all -it --rm \
  -v /path/to/host/config.py:/app/config.py \
  -v /path/to/host/myconfig.py:/app/myconfig.py \
  -v /path/to/host/tub_data:/app/tub_data \
  donkeycar-model-trainer
```

You can as well omit the --model flag and the model name will be auto created using the pattern pilot_YY-MM-DD_N.h5

Example
```bash
docker run --gpus all -it --rm \
-v ./cars/donkeypi1/vision-imitator-v1:/app/ \
-v ./cars/donkeypi1/vision-imitator-v1/data:/app/tub_data \
donkeycar-model-trainer
```

The --gpus all flag ensures that the container has access to all available GPUs. The -it flag allows interactive access to the container, and --rm automatically removes the container when it exits.

3. If you want to mount a local directory to access files from your host system inside the container, you can use the -v flag:
```bash
docker run --gpus all -it --rm -v /path/to/local/directory:/app donkeycar-model-trainer
```

Replace /path/to/local/directory with the actual path to the directory on your host system that you want to mount inside the container.

Now you have a Docker container based on the tensorflow/tensorflow:2.10.1-gpu image with Donkeycar installed. You can run your Donkeycar project inside the container, and it will have access to the GPU for accelerated computations.