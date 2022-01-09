FROM python:3-slim

# set up working directory
USER root
RUN mkdir /app
WORKDIR /app

# install requirements
COPY /app/requirements.txt /app/
RUN python3 -m pip install -r requirements.txt

# add compiled grpc to python path
ENV PYTHONPATH "${PYTHONPATH}:/grpc_compiled/"
ENV PYTHONPATH "${PYTHONPATH}:/utils/"

#CMD ["uvicorn app.main:app --host 0.0.0.0 --port 6969 --reload"] 
