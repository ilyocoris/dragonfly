FROM python:3-slim

# set up working directory
USER root
RUN mkdir /scraper
WORKDIR /scraper

# install requirements
COPY /scraper/requirements.txt /scraper/
RUN python3 -m pip install -r requirements.txt

# add compiled grpc to python path
ENV PYTHONPATH "${PYTHONPATH}:/grpc_compiled/"

# start server
# CMD [ "python3", "server.py"]
