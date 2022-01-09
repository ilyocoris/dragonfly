#!/bin/bash

# Compile all grpc-microservices protos to the grpc_compiled folder (which is binded on to the other sevrices and added to pythonpath). 
# ./protos/compile_protos.sh

python -m grpc_tools.protoc -I=protos --python_out=grpc_compiled/ --grpc_python_out=grpc_compiled/ protos/scraper.proto

python -m grpc_tools.protoc -I=protos --python_out=grpc_compiled/ --grpc_python_out=grpc_compiled/ protos/ner.proto

python -m grpc_tools.protoc -I=protos --python_out=grpc_compiled/ --grpc_python_out=grpc_compiled/ protos/sa.proto