FROM python:3-slim

# set up working directory
USER root
RUN mkdir /consumer-analyzer
WORKDIR /consumer-analyzer

# install requirements
COPY /consumer-analyzer/requirements.txt /consumer-analyzer/
RUN python3 -m pip install -r requirements.txt

# add compiled grpc to python path
ENV PYTHONPATH "${PYTHONPATH}:/grpc_compiled/"
ENV PYTHONPATH "${PYTHONPATH}:/utils/"