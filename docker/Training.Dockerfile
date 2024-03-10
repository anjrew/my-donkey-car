FROM tensorflow/tensorflow:2.10.1-gpu

# Install Donkeycar
RUN pip install donkeycar[pc]

# Set the working directory in the container
WORKDIR /app

ENV TUB_PATH="data"
ENV MODEL_NAME="model"
ENV MODEL_TYPE="linear"
ENV CONFIG_PATH="config.py"
ENV MYCONFIG_PATH="myconfig.py"
ENV FRAMEWORK="tensorflow"
ENV COMMENT="Training run started"

CMD donkey train \
    --tub "${TUB_PATH}" \
    --model "${MODEL_NAME}" \
    --type "${MODEL_TYPE}" \
    --config "${CONFIG_PATH}" \
    --myconfig "${MYCONFIG_PATH}" \
    --framework "${FRAMEWORK}" \
    --comment "${COMMENT}"