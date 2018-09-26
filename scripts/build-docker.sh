#!/bin/bash

docker build -t predixadoption/edge-hello-world:latest . --build-arg http_proxy --build-arg https_proxy
