"""
Utility functions for working with snakemake.
---------------------------------------------

This module contains utility functions for interacting with and working with snakemake.
Currently this includes functions to parse key information out of the snakemake log
file and summarize any failures.
"""

import enum
import logging
from itertools import dropwhile
from pathlib import Path
from typing import Any
from typing import ClassVar
from typing import List
from typing import Optional

import attr

# The default number of lines to return from the log files for each failed job
__LINES_PER_LOGFILE: int = 50


def last_lines(path: Path, n: Optional[int] = __LINES_PER_LOGFILE) -> List[str]:
    """Returns the last N lines from a file as a List.

    Args:
        path: the path to the file (must exist)
        n: the number of line to return, None will return all lines
    Return:
        the last n lines of the file as a list, or the whole file < n lines.
    """
    try:
        lines = read_lines(path)
        if n is not None and len(lines) > n:
            lines = lines[-n : len(lines)]
        return lines
    except Exception:
        return [f">>> Could not open log file for reading: {path}. <<<"]


def read_lines(path: Path) -> List[str]:
    """
    Reads a file and returns it as a list of lines with newlines stripped.

    Args:
        path: the path of the file to read
    Return:
        the list of lines from the file
    """
    with path.open("r") as fh:
        lines: List[str] = fh.readlines()
        return [l.rstrip() for l in lines]


def write_lines(path: Path, lines: List[str]) -> None:
    """
    Writes a list of lines to a file with newlines between the lines.

    Args:
        path:  the path to write to
        lines: the list of lines to write
    """
    with path.open("w") as out:
        for line in lines:
            out.write(line)
            out.write("\n")


@attr.s
class RuleLog:
    """Stores the path and name for the log file for a rule.

    Attributes:
        path: the path to the log file for the rule
        name: the name of the rule
    """

    path: Path = attr.ib()
    name: str = attr.ib()

    RULE_ERROR_PREFIX: ClassVar[str] = "Error in rule "
    LOG_PREFIX: ClassVar[str] = "    log: "
    LOG_SUFFIX: ClassVar[str] = " (check log file(s) for error message)"

    @classmethod
    def get_logs(cls, snakemake_log: Path) -> List["RuleLog"]:
        """Gets the logs for the rules from a Snakemake log file."""
        with snakemake_log.open("r") as fh:
            lines: List[str] = list(fh.readlines())

        logs: List[RuleLog] = []
        while lines:
            lines = list(dropwhile(lambda l: not l.startswith(cls.RULE_ERROR_PREFIX), iter(lines)))
            if lines:
                rule_name: str = lines[0].rstrip()[len(cls.RULE_ERROR_PREFIX) : -1]
                lines = list(dropwhile(lambda l: not l.startswith(cls.LOG_PREFIX), iter(lines)))
                dir: Path = Path(".").absolute()
                log_path = dir / lines[0].rstrip()[len(cls.LOG_PREFIX) : -len(cls.LOG_SUFFIX)]
                lines = lines[1:]
                logs.append(RuleLog(path=log_path, name=rule_name))

        return logs


def summarize_snakemake_errors(
    path: Path, lines_per_log: Optional[int] = __LINES_PER_LOGFILE
) -> List[str]:
    """Summarizes any errors that occurred during a run of a pipeline. Uses the snakemake log
    to find all failed rule invocations and their log files.  Produces a list of lines containing
    summary information per failed rule invocation and the last 50 lines of each log file.

    Notes:
        * fails if rule has more than one log file defined
        * fails if rule has no log file defined

    Args:
        path: the path to the main snakemake log file
        lines_per_log: the number of lines to pull from each log file, None to return all lines
    Returns:
        a list of lines containing summary information on all failed rule invocations
    """
    summary = []

    logs: List[RuleLog] = RuleLog.get_logs(snakemake_log=path)

    for log in logs:
        summary.append(f"========== Start of Error Info for {log.name} ==========")
        summary.append(f"Failed rule: {log.name}")
        summary.append(f"Last {lines_per_log} lines of log file: {log.path}")
        for line in last_lines(log.path, lines_per_log):
            summary.append(f"    {line}")
        summary.append(f"=========== End of Error Info for {log.name} ===========")

    return summary


def on_error(
    snakefile: Path,
    config: Optional[Any],
    log: Path,
    lines_per_log: Optional[int] = __LINES_PER_LOGFILE,
) -> None:
    """Block of code that gets called if the snakemake pipeline exits with an error.

     The `log` variable contains a path to the snakemake log file which can be parsed for
     more information.  Summarizes information on failed jobs and writes it to the output
     and also to an error summary file in the working directory.

     Args:
         snakefile: the path to the snakefile
         config: the configuration for the pipeline
         log: the path to the snakemake log file
         lines_per_log: the number of lines to pull from each log file, None to return all lines
     """
    try:
        # Build the preface
        preface: List[str] = [
            "Error in snakemake pipeline.",
            f"working_dir = {Path('.').absolute()}",
        ]
        # print the config attributes
        if config is not None:
            try:
                for attribute in attr.fields(type(config)):
                    value = getattr(config, attribute.name)
                    if isinstance(value, enum.Enum):
                        value = value.value
                    else:
                        value = str(value)
                    preface.append(f"{attribute.name} = {value}")
            except Exception:
                try:
                    for key, value in config.items():
                        preface.append(f"{key} = {value}")
                except Exception:
                    preface.append(f"config = {config}")
        preface.append("Detailed error information follows.")

        summary = preface + summarize_snakemake_errors(log, lines_per_log=lines_per_log)
        text = "\n".join(summary)
        pipeline_name = snakefile.with_suffix("").name
        logging.getLogger(pipeline_name).error(text)
        with Path("./error_summary.txt").open("w") as out:
            out.write(text)
    except Exception as ex:
        print("###########################################################################")
        print("Exception raised in Snakemake onerror handler.")
        print(str(ex))
        print("###########################################################################")
