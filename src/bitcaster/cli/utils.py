import logging

from colorlog import ColoredFormatter

LOGFORMAT = "%(log_color)s%(asctime)s%(reset)s | %(name)s | %(log_color)s%(message)s%(reset)s"


def configure_logging(level1, level2):
    stream = logging.StreamHandler()
    stream.setLevel(level1)
    formatter = ColoredFormatter(LOGFORMAT)
    stream.setFormatter(formatter)
    for logger_name in ["apscheduler", "dramatiq"]:
        lg = logging.getLogger(logger_name)
        lg.setLevel(level1)
        lg.addHandler(stream)
        lg.propagate = False
    for logger_name in ["bitcaster", "bitcaster.cli"]:
        lg = logging.getLogger(logger_name)
        lg.setLevel(level2)
        lg.addHandler(stream)
        lg.propagate = False
