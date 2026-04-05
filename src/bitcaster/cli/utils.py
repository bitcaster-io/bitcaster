import logging
import signal
import threading

from colorlog import ColoredFormatter

logger = logging.getLogger(__name__)

LOGFORMAT = "%(log_color)s%(asctime)s%(reset)s | %(name)s | %(log_color)s%(message)s%(reset)s"


def patch_signal():
    if threading.current_thread() is not threading.main_thread():
        # Patch signal.signal to be a no-op
        def signal_patch(signum, handler):
            logger.debug(f"Ignoring signal {signum} registration from non-main thread")

        signal.signal = signal_patch


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
