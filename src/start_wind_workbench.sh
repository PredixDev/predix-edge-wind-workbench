#!/bin/sh


echo "Wind Turbine Model"
python models/app_code.py &

PID_APP=$!

echo "Start Web Server"
python server/web_server.py &

PID_SRV=$!

echo "PID_APP : $PID_APP"
echo "PID_SRV : $PID_SRV"
