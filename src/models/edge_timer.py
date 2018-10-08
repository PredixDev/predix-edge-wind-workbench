from threading import Timer
import numbers
import sys

class PTimer(object):
    ## Perpetual Timer
    def __init__(self):
        super(PTimer,self).__init__()
        print >>sys.stderr,"INFO: PTimer initialized"
        self._thread = None
        self._thread_started = False
        self._thread_setup = False

    def setup_timer(self,rate_in_seconds,call_back):
        '''This Timer class is instanced with two parameters
        rate_in_seconds - The rate that the call back will be called,
        call_back - Call back function to call at a regular interval.'''
        self.rate_in_seconds = rate_in_seconds
        self._call_back = call_back
        self._thread = Timer(self.rate_in_seconds,self._handle_function)
        self._thread_setup = True
        self._thread_started = False

    def _handle_function(self):
        self._thread = Timer(self.rate_in_seconds,self._handle_function)
        self._thread.start()
        self._call_back()

    def start_timer(self):
        '''After this object is instanced the timer is started by calling this
        method.'''
        print >>sys.stderr,'Start timer...'
        if self._thread_setup:
            self._thread.start()
            self._thread_started = True

    def cancel_timer(self):
        '''After this object is instanced and the timer started it can be
        stoped by calling this method.'''
        if self._thread_started:
            print >>sys.stderr,'INFO: Canceling timer...'
            self._thread.cancel()
            self._thread_started = False
            self._thread_setup = False
