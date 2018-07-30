#!/bin/bash

set -e

trap "trap_ctrlc" 2

ROOT_DIR=$(pwd)

APPLICATION_ID="edge-hello-world"

curl http://localhost/api/v1/applications --unix-socket /var/run/edge-core/edge-core.sock -X POST -F "file=@/mnt/data/downloads/app.tar.gz" -H "app_name: $APPLICATION_ID"

mkdir -p /var/lib/edge-agent/app/$APPLICATION_ID/conf/

unzip /mnt/data/downloads/config.zip -d /var/lib/edge-agent/app/$APPLICATION_ID/conf/

#chown -R eauser /var/lib/edge-agent/app/$APPLICATION_ID/

if [[ $(docker service ls -f "name=$APPLICATION_ID_edge-hello-world" -q | wc -l) > 0 ]]; then
  /opt/edge-agent/app-stop --appInstanceId=$APPLICATION_ID
fi

/opt/edge-agent/app-start --appInstanceId=$APPLICATION_ID
