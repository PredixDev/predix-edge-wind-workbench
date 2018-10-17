import tornado.ioloop
import tornado.web
import tornado.websocket
from tornado import gen
import tornado.template
from tornado.escape import *
#import redis

from edgeworker import Worker, monitor_worker
from envhelpers import *

import os
import json
import sys
import os
import datetime
import signal
import math

WEBSOCKET_REFRESH_RATE_MS = 1000
FAKE_INPUT=int(os.getenv('FAKE_INPUT',0))

""" EdgeWorker interface """
ws_queues = []

class WindVizWorker(Worker):
    def initialization(self):
        self.info("WVS: Start the Wind Viz Worker")
        # Listen for new control signals
        self.add_subscription("viz_updates")
        self.add_subscription("to_ui")

    def work(self,channel,in_object):
        self.info("WVS: message received")
        json_obj = in_object
        for queue in ws_queues:
            queue.append(json_obj)
            self.info("WVS: size of queue {}".format(len(queue)))

wvw = None

@gen.coroutine
def second_loop():
    global wvw
    wvw = WindVizWorker()
    signal_handler = wvw.get_signal_handler()
    signal.signal(signal.SIGTERM, signal_handler)
    while True:
        yield gen.sleep(1)



""" Web Services """

class WT_WebSocket_Handler(tornado.websocket.WebSocketHandler):
    def open(self):
        tornado.ioloop.IOLoop.instance().add_timeout(
            datetime.timedelta(microseconds = WEBSOCKET_REFRESH_RATE_MS * 1000),
            self.update)

        self.open = True
        self.yaw = 0.0
        self.pitch = 0.0
        self.rpm = 0.0
        self.count = 0.0
        self.ws_que = []
        ws_queues.append(self.ws_que)

    def on_close(self):
        self.open = False
        ws_queues.remove(self.ws_que)

    def on_message(self, message):
        print("WVS: Message from_ui > %s" % message)
        if wvw:
            msg_obj = json.loads(message)
            wvw.publish("from_ui",msg_obj)

    def update(self):
        print("WS: Update called")
        self.count += 0.1
        try:
            dataOut = self.ws_que.pop(0)
            print("WS: Update Message:",dataOut)
        except:
            if FAKE_INPUT:
                print("WVS: Update exception executed")
                # Nothing to get in queue
                self.yaw = 180 * math.sin(self.count) + 180
                self.pitch = 2.5 * math.sin(self.count) + 3.5
                self.rpm = 10 * math.sin(self.count * 0.01) + 12

                self.wind_speed = 12 * math.sin(self.count * 0.1) + 12
                self.wind_dir = 179 * math.sin(self.count * 0.1) + 181
                self.air_density = 0.5 * math.sin(self.count * 0.01) + 1.1

                self.power = 2500000 * math.sin(self.count * 0.1) + 2500000

                dataOut = {
                    "yaw":self.yaw,
                    "pitch":self.pitch,
                    "rpm":self.rpm,
                    "wind_dir":self.wind_speed,
                    "wind_speed":self.wind_dir,
                    "air_density":self.air_density,
                    "power":self.power
                }
            else:
                dataOut = {}
        finally:
            if self.open:
                self.write_message(json.dumps(dataOut))
                tornado.ioloop.IOLoop.instance().add_timeout(
                    datetime.timedelta(microseconds = WEBSOCKET_REFRESH_RATE_MS * 1000),
                    self.update)

class WT_WebPage_Handler(tornado.web.RequestHandler):
    def get(self):
        self.render("wind_dev.html")

class WT_WebPage2_Handler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")

# *** Settings, app setup and execution
settings = {
    "template_path": './public',
    "static_path":'./public',
    "debug":True
}

application = tornado.web.Application([
    ('/',WT_WebPage2_Handler),
    ('/index.html',WT_WebPage2_Handler),
    ('/windturbine',WT_WebPage_Handler),
    ('/wt_socket',WT_WebSocket_Handler),
    ('/(.*)', tornado.web.StaticFileHandler, {"path": "./public"})
    ], **settings)

mainLoop = None

def sigterm(signum, stack):
    #print >>sys.stderr,'Docker instructed us to terminate'
    print("Docker instructed to terminate")
    if mainLoop:
        mainLoop.stop()

if __name__ == "__main__":
    #print >>sys.stderr,"Web Server......Started"
    print("Web server .... Started")
    WEB_SITE_PORT = int(os.getenv('WEB_SITE_PORT', '9005'))

    signal.signal(signal.SIGTERM, sigterm)

    application.listen(WEB_SITE_PORT)
    mainLoop = tornado.ioloop.IOLoop.instance()

    # Coroutines that loop forever are generally started with
    # spawn_callback().
    tornado.ioloop.IOLoop.current().spawn_callback(second_loop)

    mainLoop.start()
