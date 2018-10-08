import sys
import os

class Log(object):
    def __init__(self):
        super(Log, self).__init__()
        self.info("Logging init")

    def _log(self,level,string):
        self.log_level = int(os.getenv('DEBUG_ENV', 2))
        log_it = level == 'ERROR'
        log_it = log_it or (self.log_level > 0 and level == 'WARNING')
        log_it = log_it or (self.log_level > 1 and level == 'INFO')
        log_it = log_it or (self.log_level > 2 and level == 'DEBUG')
        if log_it:
            sys.stderr.write("\n%s: %s\n" % (level, string) )

    def info(self,string):
        self._log('INFO',string)

    def warning(self,string):
        self._log('WARNING',string)

    def error(self, string):
        self._log('ERROR',string)

    def debug(self, string):
        self._log('DEBUG',string)
