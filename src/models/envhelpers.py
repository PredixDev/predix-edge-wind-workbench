import os

## From stackoverflow answer
#  http://stackoverflow.com/questions/6330071/safe-casting-in-python
def safe_cast(val, to_type, default=None):
    try:
        return to_type(val)
    except (ValueError, TypeError):
        return default

def env_TEMPERATURE_UNIT():
    '''"F" returns 0, "C" returns 1, "K" returns 2. Returns "F" (0) by default'''
    return(['f','c','k'].index(os.getenv("TEMPERATURE_UNIT","F")[0].lower()))

def env_PRESSURE_UNIT():
    '''"psi" returns 0, "mbar" returns 1. Returns "psi" (0) by default'''
    return(['psi','mbar'].index(os.getenv("PRESSURE_UNIT","psi").lower()))

def env_getint(envNAME,default=0):
    '''Get an environment variable and convert to integer'''
    val = os.getenv(envNAME,str(default))
    return(safe_cast(val,int,default))

def env_getfloat(envNAME,default=0.0):
    '''Get an environment variable and convert to float'''
    val = os.getenv(envNAME,str(default))
    return(safe_cast(val,float,default))

## General Environmentla Variable helper functions

def getEnvVarStr(var_name,default=None):
    ''' Returns a single value from the environment variable 'var_name',
    if it exists, and returns it as a string else it returns default'''
    if var_name in os.environ:
        input_str = os.getenv(var_name,'_NOT_SET_USE_DEFAULT_')
        return(input_str)
    else:
        return(default)

def getEnvVarInt(var_name,default=None):
    ''' Returns a single value from the environment variable 'var_name',
    if it exists, and returns it as an integer else it returns default'''
    if var_name in os.environ:
        input_str = os.getenv(var_name,'_NOT_SET_USE_DEFAULT_')
        return(int(input_str))
    else:
        return(default)

def getEnvVarFloat(var_name,default=None):
    ''' Returns a single value from the environment variable 'var_name',
    if it exists, and returns it as a float else it returns default'''
    if var_name in os.environ:
        input_str = os.getenv(var_name,'_NOT_SET_USE_DEFAULT_')
        return(float(input_str))
    else:
        return(default)


def getEnvVarStrList(var_name,default=None):
    ''' Takes a comma separated list of string elements or a single value from the
    environment variable 'var_name', if it exists, and returns it as an list
    else it returns default'''
    if var_name in os.environ:
        input_str = os.getenv(var_name,'_NOT_SET_USE_DEFAULT_')
        if (',' in input_str):
            # this is a list of input channels to subscribe to
            return(input_str.split(','))
        else:
            # assume single channel
            # bad form fix later
            return([input_str])
    else:
        return(default)

def getEnvVarIntList(var_name,default=None):
    ''' Takes a comma separated list of integer elements or a single value from the
    environment variable 'var_name', if it exists, and returns it as an list
    else it returns default'''
    if var_name in os.environ:
        input_str = os.getenv(var_name,'_NOT_SET_USE_DEFAULT_')
        if (',' in input_str):
            # this is a list of input channels to subscribe to
            input_list = input_str.split(',')
            return([int(x) for x in input_list])
        else:
            # assume single channel
            # bad form fix later
            return([int(input_str)])
    else:
        return(default)

def getEnvVarFloatList(var_name,default=None):
    ''' Takes a comma separated list of float elements or a single value from the
    environment variable 'var_name', if it exists, and returns it as an list
    else it returns default'''
    if var_name in os.environ:
        input_str = os.getenv(var_name,'_NOT_SET_USE_DEFAULT_')
        if (',' in input_str):
            # this is a list of input channels to subscribe to
            input_list = input_str.split(',')
            return([float(x) for x in input_list])
        else:
            # assume single channel
            # bad form fix later
            return([float(input_str)])
    else:
        return(default)

def getEnvVarListFromPattern(var_name_start_pattern,default=None):
    ''' Returns a list of values from the environment variables that have a
    starting string pattern that matches 'var_name_start_pattern',
    if they exist, else returns default
    Use: Get a list of items from environment variables that may be to
    long for a single environment variable (See egdin_real for example)'''
    envVarList = []
    # Look at environment variables
    for key in os.environ:
        if key.startswith(var_name_start_pattern):
            env_str = os.environ[key]
            envVarList.append(env_str)
    if len(envVarList) != 0:
        return(envVarList)
    else:
        return(default)

def list_to_list_of_dict(string_list):
    ''' Takes list of strings that are the json form of a dictionary and
    converts these to a list of dictionaries. Useful for getting the definition
    of objects from environmnet variables.
    See 'example_getting_xsignal_from_env' code, below, for example'''
    out_list = []
    for string in string_list:
        out_list.append(json.loads(string))
    return(out_list)

def example_getting_xsignal_from_env():
    ''' Example of how to get a list of objects from environment variables'''
    xsignals_str_list = getEnvVarListFromPattern('XSIGNAL_',[])
    signal_reqs_list = list_to_list_of_dict(xsignals_str_list)
    return(signal_reqs_list)
    ''' The environment variables would look like this:

    XSIGNAL_01='{"type":"sine", "tag":"sine_1", "amplitude":50.0, \
                  "frequency":1, "phaserads":0, "offset":0 ,"min":-45.0, \
                  "max":45.0}'
    XSIGNAL_02='{"type":"sine", "tag":"sine_2", "amplitude":70.0, \
                  "frequency":0.5, "phaserads":0, "offset":0 ,"min":-45.0, \
                  "max":45.0}'
    XSIGNAL_03='{"type":"sine", "tag":"sine_3", "amplitude":900.0, \
                  "frequency":0.01, "phaserads":0, "offset":0 ,"min":-45.0, \
                  "max":45.0}'
    XSIGNAL_04='{"type":"randomwalk", "tag":"rw_1", \
                  "initval":50.0 ,"min":0.0, "max":100.0, \
                  "randswing":10.0}'
    XSIGNAL_05='{"type":"randomwalk", "tag":"rw_2",
                  "initval":51.0 ,"min":0.0, "max":60.0, \
                  "randswing":5.0}'
    XSIGNAL_06='{"type":"randomwalk", "tag":"rw_3", \
                  "initval":25.0 ,"min":0.0, "max":75.0, \
                  "randswing":9.0}'
    '''
