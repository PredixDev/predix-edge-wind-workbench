import paho.mqtt.client as mqtt
import json
import time

client = mqtt.Client()

def on_connect(client, userdata, flags, rc):
  print("Connected with result code "+str(rc))

class MQTTClient():
    def __init__(self):
        #client.on_connect = on_connect
        #client.connect("mqtt-tcp://predix-edge-broker")
        client.connect("localhost",1883,60)
        client.on_connect = on_connect
    def pub(to_channel,data_str):
        print "Sending data : "+data_str
        client.publish("topic/test", payload=data_str, qos=0, retain=False)

if __name__ == '__main__':
    # Create and start the worker
    mqttclient = MQTTClient()
    mqttclient.pub("test")
