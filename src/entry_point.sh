#!/bin/sh
echo "Setting time zone to '${TIME_ZONE}'"

cp /usr/share/zoneinfo/${TIME_ZONE} /etc/localtime
echo "${TIME_ZONE}" >/etc/timezone

cd /opt/microservice
echo "Wind Turbine Model"
exec python app_code.py &

PID_APP=$!

cd /opt/server
echo "Start Web Server"
exec python web_server.py &

PID_SRV=$!

trap 'kill $PID_APP;kill $PID_SER' EXIT

wait
