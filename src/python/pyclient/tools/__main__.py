"""Main entry point for all pyclient tools."""

import logging
import sys
from typing import Callable
from typing import List

import defopt

from pyclient.tools.hello_world import hello_world

TOOLS: List[Callable] = sorted(
    [hello_world], key=lambda f: f.__name__,
)


def main(argv: List[str] = sys.argv[1:]) -> None:
    logger = logging.getLogger(__name__)
    if len(argv) != 0 and all(arg not in argv for arg in ["-h", "--help"]):
        logger.info("Running command: client-tools " + " ".join(argv))
    try:
        defopt.run(funcs=TOOLS, argv=argv)
        logger.info("Completed successfully.")
    except Exception as e:
        logger.info("Failed on command: " + " ".join(argv))
        raise e
