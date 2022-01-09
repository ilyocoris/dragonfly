FROM huggingface/transformers-cpu

# set up working directory
USER root
RUN mkdir /sa
WORKDIR /sa

# install requirements
COPY /sa/requirements.txt /sa/
RUN python3 -m pip install -r requirements.txt

# add compiled grpc to python path
ENV PYTHONPATH "${PYTHONPATH}:/grpc_compiled/"
