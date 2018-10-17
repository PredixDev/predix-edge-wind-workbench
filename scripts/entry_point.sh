#!/bin/sh

env
export CDP_CONFIG=/opt/cdp_config/cdp_config.json
ls -lrt /opt/cdp_config
cat $CDP_CONFIG

cd /opt/microservice
echo "Wind Turbine Model..."
exec python app_code.py &

PID_APP=$!

trap 'kill $PID_APP' EXIT

cd /opt/webserver
echo "Start Web Server..."
exec python web_server.py &

PID_SRV=$!

trap 'kill $PID_SRV' EXIT

wait
