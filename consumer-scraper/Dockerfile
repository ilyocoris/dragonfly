FROM python:3-slim

# set up working directory
USER root
RUN mkdir /consumer-scraper
WORKDIR /consumer-scraper

# install requirements
COPY /consumer-scraper/requirements.txt /consumer-scraper/
RUN python3 -m pip install -r requirements.txt

# add compiled grpc to python path
ENV PYTHONPATH "${PYTHONPATH}:/grpc_compiled/"
ENV PYTHONPATH "${PYTHONPATH}:/utils/"