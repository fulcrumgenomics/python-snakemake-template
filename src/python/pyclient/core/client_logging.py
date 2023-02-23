"""
Methods for setting up logging for tools.
-----------------------------------------
"""

import logging
import socket
from threading import RLock


# Global that is set to True once logging initialization is run to prevent running > once.
__PYCLIENT_LOGGING_SETUP: bool = False

# A lock used to make sure initialization is performed only once
__LOCK = RLock()


def setup_logging(level: str = "INFO") -> None:
    """Globally configure logging for all modules under pyclient.

    Configures logging to run at a specific level and output messages to stderr with
    useful information preceding the actual log message.
    """
    global __PYCLIENT_LOGGING_SETUP

    with __LOCK:
        if not __PYCLIENT_LOGGING_SETUP:
            client_format = (
                f"%(asctime)s {socket.gethostname()} %(name)s:%(funcName)s:%(lineno)s "
                + "[%(levelname)s]: %(message)s"
            )
            handler = logging.StreamHandler()
            handler.setLevel(level)
            handler.setFormatter(logging.Formatter(client_format))

            logger = logging.getLogger("pyclient")
            logger.setLevel(level)
            logger.addHandler(handler)
        else:
            logging.getLogger(__name__).warning("Logging already initialized.")

        __PYCLIENT_LOGGING_SETUP = True
