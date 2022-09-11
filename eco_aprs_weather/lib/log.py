
"""
centralized logging module
import throughout your application by using
# import logging
# logger = logging.getLogger(__name__)
# logger.debug("test")
# logger.info("test")
# logger.warning("test")
# logger.error("test")
# logger.exception("test")
"""

import logging
import logging.config


class AnsiColor(object):
    """
    life is better in color
    """
    header = '\033[95m'
    blue = '\033[1;94m'
    green = '\033[1;92m'
    yellow = '\033[93m'
    red = '\033[91m'
    end = '\033[0m'
    bold = '\033[1m'
    underline = '\033[4m'

class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances.keys():
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class LoggerManager(object):
    __metaclass__ = Singleton

    _loggers = {}

    def __init__(self, *args, **kwargs):
        pass

    @staticmethod
    def getLogger(name=None):
        format=('{blue1}%(asctime)s '
                '{red1}%(filename)s:%(lineno)d '
                '{yel1}%(levelname)s '
                '{gre1}%(funcName)s '
                '{res}%(message)s').format(blue1=AnsiColor.blue, red1=AnsiColor.red, yel1=AnsiColor.yellow, res=AnsiColor.end, gre1=AnsiColor.green)
        if not name:
            logging.basicConfig(format=format)
            return logging.getLogger()
        elif name not in LoggerManager._loggers.keys():
            logging.basicConfig(format=format)
            LoggerManager._loggers[name] = logging.getLogger(str(name))
        return LoggerManager._loggers[name]

log=LoggerManager().getLogger("eco_aprs_weather")
log.setLevel(level=logging.DEBUG)