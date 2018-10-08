from edgeworker import Worker, worker_monitor
import time

######################################################################
#### Testing
#### Need redis or what ever CDP you are using available
######################################################################
if __name__ == "__main__":
    ## SSX is a dummy Simulink class
    ## you may want to set the REDIS_PY_IP env var
    #  on Mac use setnv REDIS_PY_IP 127.0.0.1
    class SSX(object):
        def __init__(self):
            super(SSX, self).__init__()
            print "SSX has initialized"

        def set_SSX_value_a(self,a):
            print "SSX >a< set",a
            self.a = a

        def set_SSX_value_b(self,b):
            print "SSX >b< set",b
            self.b = b

        def step(self):
            print "SSX step called"
            self.x = self.a + self.b

        def get_SSX_value_x(self):
            return(self.x)

        def terminate(self):
            print "SSX has been terminated"
            # call the terminate function of the parent
            super(SSX,self).terminate()

    ## Very simple micro-service
    class TestWorkerA(SSX,Worker):
        def initialization(self):
            print "TestWorkerA initialization"
            self.in_channel = None
            self.in_object = None

        def work(self,channel,in_object):
            print "TestWorkerA on channel",channel,"recieved",in_object
            self.in_channel = channel
            self.in_object = in_object

    ## Micro-service that is similar to those used in the Simulink pipeline
    class TestWorkerB(SSX,Worker):
        def initialization(self):
            print "TestWorkerB initialization"
            self.in_channel = None
            self.in_object = None

        def work(self,channel,in_object):
            kv_object = self.get('ssx_test_in_a')
            self.set_SSX_value_a(kv_object['a'])
            self.set_SSX_value_b(in_object['b'])
            self.step()
            out_object = {}
            out_object['x'] = self.get_SSX_value_x()
            self.set('ssx_test_out_x',out_object)

    ## Micro-service to test the perpetual timer
    class TestWorkerC(Worker):
        def initialization(self):
            print "TestWorkerC initialization"
            self.count = 0
            time_in_seconds = 1
            self.setup_timer(time_in_seconds,self.worker_timer)
            self.start_timer()

        def work(self,channel,in_object):
            print "No one will call this becuase there are no subscriptions"

        def worker_timer(self):
            self.count = self.count + 1


    tests_passed = 0
    # Test edgeworker
    twa = TestWorkerA()
    twb = TestWorkerB()

    print "******************************************************************************"
    print "TEST: pub/sub TWB -> TWA *****************************************************"
    print
    print "TWA subscribe to channel FOR_A"
    print
    twa.add_subscription('FOR_A')
    print "TWB publish to FOR_A"
    print
    twb.publish("FOR_A",{'data':'from b'})
    print "Should see a print from TWA now"
    print
    time.sleep(0.2)
    print "Checking results"
    test_result = False
    print "in_channel",twa.in_channel,"in_object",twa.in_object
    try:
        test_result = (twa.in_channel == 'FOR_A' and twa.in_object['data'] == 'from b')
    except:
        pass
    if test_result:
        print "GOOD: Pub/sub from TWB to TWA passed"
        tests_passed += 1
    else:
        print "BAD: Pub/sub from TWB to TWA failed"
        exit(0)
    print
    print

    print "******************************************************************************"
    print "TEST: pub/sub TWB -> TWA wrong channel (Should fail)**************************"
    print
    print "TWA subscribe to channel FOR_A"
    print
    twa.add_subscription('FOR_A')
    print "twb publish to FOR_XXXXXX"
    print
    twb.publish("FOR_XXXXXX",{'data':'from xxxxx'})
    print "Should not see a print from TWA now"
    print
    time.sleep(0.2)
    print "Check results"
    try:
        test_result = (twa.in_channel == 'FOR_A' and twa.in_object['data'] == 'from b')
    except:
        pass
    if test_result:
        print "GOOD: Pub/sub to wrong channel from TWB to TWA passed"
        tests_passed += 1
    else:
        print "BAD: Pub/sub from TWB to TWA failed"
        exit()

    print
    print "******************************************************************************"
    print "TEST: key/value TWB -> TWA ***************************************************"
    print
    print "TWB set key 'testkv' to {'data':12}"
    twb.set('testkv',{'data':12})
    print "TWA read key"
    print
    print "Received ",twa.get('testkv')
    test_object = twa.get('testkv')
    test_result = False
    try:
        test_result = (test_object['data'] == 12)
    except:
        pass
    if test_result:
        print "GOOD: K/V from TWB to TWA passed"
        tests_passed += 1
    else:
        print "BAD: K/V from TWB to TWA failed"
        exit()

    print "******************************************************************************"
    print "TEST: pub/sub and key/value plus Simulink proxy calculation TWA -> TWB *******"
    print
    print "TWA set key 'ssx_test_in_a' to {'a':12}"
    twa.set('ssx_test_in_a',{'a':12})
    print
    print "Setup channel in B"
    twb.add_subscription('FOR_B')
    print
    print "Publish a {'b':2} to FOR_B"
    twa.publish('FOR_B',{'b':2})
    print
    print "Delay 0.2 seconds"
    time.sleep(0.2)
    print
    print "Get ssx_test_out_x result from k/v"
    print "Result:",twb.get('ssx_test_out_x')
    test_object = twb.get('ssx_test_out_x')
    test_result = False
    try:
        test_result = (test_object['x'] == 14)
    except:
        pass
    if test_result:
        print "GOOD: K/V from TWB to TWA passed"
        tests_passed += 1
    else:
        print "BAD: K/V from TWB to TWA failed"
        exit()

    print "******************************************************************************"
    print "TEST: Timer function *******"
    print
    print "Instance TWC which has a 1 second timer that increases a counter by 1"
    twc = TestWorkerC()
    print
    print "Get the value of the counter"
    early_count = twc.count
    print "Early count:",early_count
    print
    print "Delay for 4 seconds"
    time.sleep(4)
    print
    print "Get the value of the counter again"
    late_count = twc.count
    print "Late count:",late_count
    print
    print "Check values"
    test_result = False
    try:
        test_result = (early_count < late_count)
    except:
        pass
    if test_result:
        print "GOOD: Timer and counter working"
        tests_passed += 1
    else:
        print "BAD: Counter or Timer failed"
        exit()

    if (tests_passed == 5):
        print "******************************************************************************"
        print "******************************************************************************"
        print "******************************************************************************"
        print "GOOD: ALL TESTS PASSED"
        print "******************************************************************************"
        print "******************************************************************************"
        print "******************************************************************************"
    else:
        print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<"
        print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<"
        print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<"
        print "BAD: ALL TESTS DID NOT PASS"
        print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<"
        print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<"
        print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<"

    twa.terminate()
    twb.terminate()
    twc.terminate()

    # Need to figure out how to test these
    #worker_monitor(twa)
    #worker_monitor(twb)
    #worker_monitor(twc)
