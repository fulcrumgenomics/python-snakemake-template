import logging
from pathlib import Path

from toolkit.tools import CommonOptions
from toolkit.tools import Tool

LOGGER_NAME = "example"


def example(
    *,
    input_file: str | Path,
    output_file: str | Path,
    _common_opts: CommonOptions = None,
) -> None:
    """
    Copies data from an input file to an output file.

    Args:
        input_file: Path to the input file
        output_file: Path to the output file
    """
    log = logging.getLogger(LOGGER_NAME)

    log.info(f"Reading input from {input_file} to {output_file}...")

    with open(input_file) as inp, open(output_file, "w") as out:
        for line in inp:
            print(line, file=out)


def tool() -> Tool:
    return Tool(
        example,
        "example",
        "Do an awesome thing.",
        short_options={
            "input-file": "i",
            "output-file": "o",
        },
    )
