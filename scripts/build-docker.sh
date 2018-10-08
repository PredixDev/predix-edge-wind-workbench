#!/bin/bash

docker build -t predixadoption/edge-hello-world:latest . --build-arg http_proxy --build-arg https_proxy --build-arg no_proxy --build-arg ARTIFACTORY_USER --build-arg ARTIFACTORY_PASS

docker pull dtr.predix.io/predix-edge/predix-edge-mosquitto-amd64:latest

docker stack deploy -c docker-compose-edge-broker.yml predix-edge-broker

docker stack deploy -c docker-compose-local.yml edge-hello-world

docker service ls

docker service logs edge-hello-world_edge-hello-world
