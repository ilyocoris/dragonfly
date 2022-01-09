FROM jupyter/base-notebook

USER root
RUN mkdir /workspace
RUN mkdir /workspace/notebooks
WORKDIR /workspace

# install requirements
COPY /notebooks/requirements.txt .
RUN python3 -m pip install -r requirements.txt

# add compiled grpc to python path
ENV PYTHONPATH "${PYTHONPATH}:/grpc_compiled/"
ENV PYTHONPATH "${PYTHONPATH}:/utils/"

# run notenook
# CMD ["jupyter", "notebook", "--allow-root", "--notebook-dir=.", "--ip=0.0.0.0", "--port=8888", "--no-browser"]