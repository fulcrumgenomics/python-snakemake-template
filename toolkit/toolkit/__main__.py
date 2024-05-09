import logging
import sys
import textwrap
from enum import Enum
from pathlib import Path
from typing import Iterator

import defopt

from toolkit.lib import log
from toolkit.lib import utils
from toolkit.tools import CommonOptions
from toolkit.tools import example

LOGGER_NAME = "toolkit"


class Command(Enum):
    """
    Enumeration of sub-commands that can be executed from this script.
    """

    example = example.tool()

    @staticmethod
    def doc() -> str:
        """
        Returns command documentation suitable for inserting into `main`'s docstring.
        """
        return textwrap.indent(
            "\n".join(f"* {v.name}\t{v.value.description}" for v in Command), ""
        )


@utils.format_doc(commands=Command.doc())
def main(
    command: Command,
    *,
    log_level: log.LogLevel = log.LogLevel.INFO,
    log_file: Path | None = None,
    no_log: bool = False,
    overwrite: bool = False,
) -> CommonOptions:
    """
    Client pipeline tools.

    commands:
    {commands}

    .. The `command` parameter is not used - it is only present so it will appear in the
       help message.

    Args:
        command: the command to execute.

    Keyword Arguments:
        log_level: minimum level to log.
        log_file: Path to the log file. By default, the log is written to stderr. Use the
            '--no-log' flag to disable writing the log.
        no_log: Do not write logging information. Messages with level 'ERROR' and above are still
            written to stderr.
        overwrite: Overwrite existing output files. By default, the program exits with an error
            if an output already exist.
    """
    if no_log:
        logging.disable(logging.WARNING)
    else:
        log.init_logging(log_level, log_file, overwrite)

    return CommonOptions(overwrite)


def handle_main() -> tuple[list[str], int | None, CommonOptions]:
    """
    Parse command-line options that are common to all commands.

    Common options appear between the script name and the command name. For example, in the
    following command, '--log-level DEBUG' is a common option, 'doit' is the command, and
    '--name foo' is an option specific to the 'doit' command.

    ::
        python my_script.py --log-level DEBUG doit --name foo

    Returns:
        argv: the command-line arguments.
        command_idx: the index of the command in argv (>= 1), or `None` if no command was
            specified.
    """
    argv = sys.argv
    command_names = set(v.name for v in Command)
    command_idx = None
    for i in range(1, len(argv)):
        if argv[i] in command_names:
            command_idx = i
            break

    common_argv = argv[1:command_idx] if command_idx else argv[1:]
    # have to provide a command name, but it's ignored
    common_opts = defopt.run(main, argv=common_argv + [next(iter(command_names))])
    return argv, command_idx, common_opts


def merge_short_options(dicts: Iterator[dict[str, str | None]]) -> dict[str, str]:
    param_to_opt = {}
    opt_to_param = {}
    for d in dicts:
        for param, opt in d.items():
            assert opt is not None

            if param not in param_to_opt:
                param_to_opt[param] = opt
            elif param_to_opt[param] != opt:
                raise ValueError(
                    f"Parameter '{param}' defined with different short options: "
                    f"'{param_to_opt[param]}' and '{opt}'"
                )

            if opt not in opt_to_param:
                opt_to_param[opt] = param
            elif opt_to_param[opt] != param:
                raise ValueError(
                    f"Short option '{opt}' used for multiple parameters: "
                    f"'{opt_to_param[opt]}' and '{param}'"
                )

    return param_to_opt


def run() -> None:
    argv, command_idx, common_opts = handle_main()
    if command_idx:
        commands = dict((v.name, v.value.fn) for v in Command)
        command_argv = argv[command_idx:]
        short_options = merge_short_options(
            v.value.short_options for v in Command if v.value.short_options is not None
        )
        command = defopt.bind(
            commands, short=short_options, argv=command_argv, no_negated_flags=True
        )
        # Some versions of defopt wrap the partial function call in a way that additional
        # arguments cannot be specified, so we have to unwrap it
        if hasattr(command, "__wrapped__"):
            command = command.__wrapped__
        if "-h" in command_argv:
            # don't log anything if we're printing a help message
            command()
        else:
            log = logging.getLogger(LOGGER_NAME)
            log.info(f"Executing: {' '.join(argv)}")
            try:
                command(_common_opts=common_opts)
                log.info("Finished executing successfully.")
            except Exception:
                log.critical("Execution failed", exc_info=True)
                sys.exit(1)


if __name__ == "__main__":
    run()
