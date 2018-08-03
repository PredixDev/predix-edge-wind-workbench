#!/bin/bash

set -x

trap "trap_ctrlc" 2

APPLICATION_ID="edge-hello-world"
APP_SERVICE_NAME="$APPLICATION_ID_$APPLICATION_ID"
HELLO_WORLD_APP="hello-world-app.tar.gz"
HELLO_WORLD_CONFIG="hello-world-config.zip"

ROOT_DIR=$(pwd)
echo $APP_SERVICE_NAME
if [[ $(docker service ls -f "name=$APP_SERVICE_NAME" -q | wc -l) -eq 1 ]]; then
  docker service rm "$APP_SERVICE_NAME"
  echo "Edge Hello world service removed"
else
  echo "Edge Hello world service not found"
fi


mkdir -p /var/lib/edge-agent/app/$APPLICATION_ID/conf/
rm -rf /var/lib/edge-agent/app/$APPLICATION_ID/conf/*
unzip /mnt/data/downloads/$HELLO_WORLD_CONFIG -d /var/lib/edge-agent/app/$APPLICATION_ID/conf/

#/opt/edge-agent/app-start --appInstanceId=$APPLICATION_ID

#if [[ $(curl http://localhost/api/v1/applications --unix-socket /var/run/edge-core/edge-core.sock -X POST -F "file=@/mnt/data/downloads/$HELLO_WORLD_APP" -H "app_name: $APPLICATION_ID") ]]; then
/opt/edge-agent/app-deploy --enable-core-api $APPLICATION_ID /mnt/data/downloads/$HELLO_WORLD_APP

if [[ $(docker service ls -f "name=$APP_SERVICE_NAME" -q | wc -l) > 0 ]]; then
  echo "Edge Hello world service started"
fi

docker service logs $(docker service ls -f "name=$APP_SERVICE_NAME" -q) >> /mnt/data/downloads/quickstart.log
