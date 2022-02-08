FROM python:3-slim

# set up working directory
USER root
RUN mkdir /ner
WORKDIR /ner

# install requirements
COPY /ner/requirements.txt /ner/
RUN python3 -m pip install -r requirements.txt

# add compiled grpc to python path
ENV PYTHONPATH "${PYTHONPATH}:/grpc_compiled/"

# start server
# CMD [ "python3", "server.py"]
