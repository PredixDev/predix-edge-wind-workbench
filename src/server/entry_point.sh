#!/bin/sh
cd /opt/webserver
echo "Start Web Server"
exec python web_server.py &

PID_SRV=$!

trap 'kill $PID_SRV' EXIT

wait
