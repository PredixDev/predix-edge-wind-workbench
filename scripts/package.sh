#!/bin/bash

docker save -o images.tar predixadoption/edge-hello-world:latest dtr.predix.io/predix-edge/predix-edge-mosquitto-amd64:latest

tar -czvf app.tar.gz images.tar docker-compose.yml

cd config
zip -X -r ../config.zip *.json
cd ../
