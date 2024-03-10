FROM tensorflow/tensorflow:2.10.1-gpu

# Install Donkeycar
RUN pip install donkeycar[pc]

# Set the working directory in the container
WORKDIR /app



# Specify the command to run when the container starts
CMD [ \
"donkey", \
"train", \
"--tub", "tub_data", \
"--model", "my_model", \
"--type", "linear", \
"--config", "config.py", \
"--myconfig", "myconfig.py", \
"--framework", "tensorflow", \
"--comment", "My training run" \
]