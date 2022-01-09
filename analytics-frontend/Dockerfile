FROM python:3-slim

# set up working directory
USER root
RUN mkdir /analytics-frontend
WORKDIR /analytics-frontend

# install requirements
COPY /analytics-frontend/requirements.txt /analytics-frontend/
RUN python3 -m pip install -r requirements.txt



# start server
# CMD [ "python3", "server.py"]
