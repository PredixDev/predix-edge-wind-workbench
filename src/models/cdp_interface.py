import threading
import json
import os
import sys
import signal
import types
import time
#import MQTTClient
import traceback
#from config_helper import *

class CDPInterface(threading.Thread):

    def __init__(self):
        super(CDPInterface, self).__init__()
        print >>sys.stderr,"INFO: Init CDPInterface"
        cdp_config = self._get_cdp_config()
        print >>sys.stderr,"INFO: CDP config %s" % cdp_config
        self._term_event = threading.Event()

        self.daemon = True # so we can kill it with CTRL-C
        # Create the CDP object and a registry entry for a REDIS transport
        self.cdp = pycdp.pycdp(cdp_config, log_level=pycdp.log_warn, log_id="test")
        #self.cdp = new MQTTClient()
        self.in_channels = []

    def publish(self, to_channel, data_obj, parse_type="json"):
        """Publishes an object, 'data_obj' 'to_channel' of the CDP. Expects that
           'data_obj' is an object that can be serialized by Python's 'json' library unless
           'parse-type' is 'raw' then will be published as string. Expects that 'to_channel' is a string."""
        if (parse_type == "json"):
            json_str = json.dumps(data_obj)
            self.cdp.pub(to_channel, json_str)
        elif (parse_type == "raw"):
            data_str = str(data_obj)
            self.cdp.pub(to_channel, data_str)
        else:
            print >>sys.stderr, 'INFO: Incompatible data parse type "%s"' % parse_type
            sys.exit(1)

    def add_subscription(self,channels, parse_type="json"):
        """Subscribes to pub/sub either a single or list of channels. Expects
           strings."""

        if isinstance(channels,list):
            for channel in channels:
                self._append_in_channel(channel, parse_type)
        elif isinstance(channels,types.StringTypes):
            self._append_in_channel(channels, parse_type)
        else:
            print >>sys.stderr, "ERROR: 'cdp_interface.py's 'subscribe' doesn't"
            print >>sys.stderr, "       handle channels of type {}.".format(type(channels))
            print >>sys.stderr, "       ",str(channels)
            print >>sys.stderr, "       Needs to be fixed EXITING..."
            sys.exit(1)

    def _append_in_channel(self, channel, parse_type):
        self.in_channels.append(channel)

        if (parse_type == "json"):
            s = self.cdp.sub(channel, self._sub_handler_json)
        elif (parse_type == "raw"):
            s = self.cdp.sub(channel, self._sub_handler_raw)
        else:
            print >>sys.stderr, 'INFO: Incompatible data parse type "%s"' % parse_type
            sys.exit(1)

        print >>sys.stderr, "INFO: Subscription to %s was added" % channel
        print >>sys.stderr, "INFO: Channel subsrciption code ", s

    def set(self, key, data_obj, parse_type="json"):
        """Pushes an object, 'data_obj', to CDP pointed to by 'key'. The object
           must be of a type that can be serialized to JSON via Python's 'json'
           library unless 'parse-type' is 'raw' then will be set as string."""
        if (parse_type == "json"):
            json_str = json.dumps(data_obj)
            #TODO: handle json conversion exceptions
            self.cdp.set(key, json_str)
        elif (parse_type == "raw"):
            data_str = str(data_obj)
            self.cdp.set(key, data_str)
        else:
            print >>sys.stderr, 'INFO: Incompatible data parse type "%s"' % parse_type
            sys.exit(1)

    def get(self, key, parse_type="json"):
        """Returns the string value pointed at by 'key' from CDP. Expects that
           'key' is a string."""
        (status, m) = self.cdp.get(key)
        if status != 200:
            print >>sys.stderr, "INFO: CDP Error get() [%d] Missing key: %s" % (status, key)
            return None
        if (parse_type == "json"):
            try:
                json_obj = json.loads(m)
                return(json_obj)
            except:
                print >>sys.stderr, "INFO: CDP Error Get() exception:", traceback.format_exc()
        elif (parse_type == "raw"):
            return m
        else:
            print >>sys.stderr, 'INFO: Incompatible data parse type "%s"' % parse_type
            sys.exit(1)

        return None

    def exists(self, key):
        """ Given a 'key' string determine if the key exists in the CDP (could it
            be retrieved via a 'get' or 'gets')."""
        (status, m) = self.cdp.get("/exists?key=%s" % (key))
        if status != 200:
            print >>sys.stderr, "INFO: CDP query exists not successful--code: [%d] key: %s" % (status, key)
            return False
        else:
            #print >>sys.stderr, "CDP: query exists code: [%d],  key: %s, message %s" % (s, key, m)
            if int(m) == 1:
                return True
            return False

    def sets(self, key, strval):
        """This function pushes 'strval' to CDP without JSON conversion. Expects
           'key' and 'strval' to be strings. Doesn't do a serialization."""
        self.cdp.set(key, strval)

    def gets(self, key):
        """Returns the string value pointed at by 'key' from CDP. Expects that
           'key' is a string. Doesn't do deserialization."""
        (status, m) = self.cdp.get(key)
        if status != 200:
            print >>sys.stderr, "INFO: CDP Error get() [%d] Missing key: %s" % (status, key)
            return None
        return(m)

    def keys(self, key_pattern):
        """Returns a list of keys that match 'key_pattern'. Expects 'key_pattern'
           to be a string and that this string is a regex."""
        ## Returns of matching keys
        (status,m) = self.cdp.get("/keys?pattern=%s" %(key_pattern))
        key_list = json.loads(m)
        return key_list

    def cancel_cdp(self):
        self._term_event.set()

    def cdp_is_terminated(self):
        return self._term_event.is_set()

    def _sub_handler_json(self, source, channel, raw_message):
        try:
            json_obj = json.loads(raw_message)  # need better error handling
        except:
            print >>sys.stderr, "ERROR: On channel %s json.loads %s" % (channel, str(sys.exc_info()[0]))
            return

        try:
            #print >>sys.stderr, "DEBUG", channel, json_obj
            # Notice Calls the derived class version of work
            self.work(channel, json_obj)
        except:
            print >>sys.stderr, "DEBUG: Exception calling work", traceback.format_exc()

    def _sub_handler_raw(self, source, channel, raw_message):
        try:
            #print >>sys.stderr, "DEBUG", channel, raw_message
            # Notice Calls the derived class version of work
            self.work(channel, raw_message)
        except:
            print >>sys.stderr, "DEBUG: Exception calling work", traceback.format_exc()

    def run(self):
        # This gets called by a call to threads start routine
        while not self.cdp_is_terminated():
            time.sleep(0.01)  # be nice to the system :)
        print >>sys.stderr, "INFO: run thread terminated"


    def _external_cdp_config(self):
        # check Environment variable CDP_CONFIG first
        # if not exist, try to load config.json file
        # if not successful, return None for _get_cdp_config() processing
        cdp_config = os.getenv('CDP_CONFIG', None)
        if cdp_config == None:
            try:
                cdp_config_path = os.getenv("CDP_CONFIG_PATH", 'config/cdp_config.json')
                #cdp_config_path = file_for_site_management(cdp_config_path)
                print "DEBUG: cdp_config_path is %s" %cdp_config_path
                with open (cdp_config_path) as cdp_config_file:
                    cdp_config = json.dumps(json.load(cdp_config_file))
                    print "DEBUG: print config file: %s" %cdp_config
            except:
                print >>sys.stderr, "INFO: could not load CDP_CONFIG from %s, use default cdp_config." % cdp_config_path
                return None
        return cdp_config

    def _get_cdp_config(self):
        cdp_config = self._external_cdp_config()
        if cdp_config == None:
            cdp_config = json.dumps({
                  "info":{
                    "file_version":1.0
                  },
                  "config":{
                    "plane1":{
                    "transport_addr":"redis://edgeservices_cdp_redis"
                    },
                    "plane2":{
                    "transport_addr":"mqtt-tcp://edgeservices_cdp_mqtt"
                    }
                  },
                  "mapping":[
                    ["plane1",12, ".*", ""],
                    ["plane2",3, ".*", ""]
                  ]
            })
        return cdp_config
