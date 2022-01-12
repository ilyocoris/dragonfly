FROM python:3-slim

# set up working directory
USER root
RUN mkdir /analytics-frontend
WORKDIR /analytics-frontend

# install requirements
COPY /analytics-frontend/requirements.txt /analytics-frontend/
RUN python3 -m pip install -r requirements.txt

# add utils to pythonpath
ENV PYTHONPATH "${PYTHONPATH}:/utils/"