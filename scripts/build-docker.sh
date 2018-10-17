#!/bin/bash

SKIP_BROWSER=0

#docker rmi predixadoption/edge-hello-world:latest -f

docker build  --no-cache -t predixadoption/edge-hello-world:1.0.31 -f ./Dockerfile . --build-arg http_proxy --build-arg https_proxy --build-arg no_proxy
docker pull dtr.predix.io/predix-edge/predix-edge-mosquitto-amd64:latest

docker stack deploy -c docker-compose-edge-broker.yml predix-edge-broker

docker stack deploy -c docker-compose-local.yml edge-hello-world

sleep 20

docker service ls

docker service logs edge-hello-world_edge-hello-world

# Automagically open the application in browser, based on OS
if [[ $SKIP_BROWSER == 0 ]]; then
  app_url="http://127.0.0.1:9098"

  case "$(uname -s)" in
     Darwin)
       # OSX
       open $app_url
       ;;
     Linux)
       # LINUX
       if [[ $( which xdg-open | wc -l ) == 1 ]]; then
          xdg-open $app_url
       fi
       ;;
     CYGWIN*|MINGW32*|MINGW64*|MSYS*)
       # Windows
       start "" $app_url
       ;;
  esac
fi
