"""Tests for pipelines within :module:`~pyclient`

The tests briefly test the Snakefiles to ensure they are runnable and generally execute the
expected rules.  They are far from comprehensive, as they do not verify the analytical results
of each pipeline, which should be done elsewhere.
"""


from collections import defaultdict
from pathlib import Path
from typing import Any
from typing import Callable
from typing import Dict
from typing import List
from typing import Optional

import snakemake


class SnakemakeLogger(object):
    """Returns a log handler for snakemake and tracks if the rules that were run"""

    def __init__(self) -> None:
        self.rule_count: Dict[str, int] = defaultdict(lambda: 0)

    def log_handler(self) -> Callable[[Dict[str, Any]], None]:
        """Returns a log handler for use with snakemake."""

        def fn(d: Dict[str, Any]) -> None:
            if d["level"] != "run_info":
                return
            # NB: skip the first three and last lines
            for counts_line in d["msg"].split("\n")[3:-1]:
                counts_line = counts_line.strip()
                job, count, min_threads, max_threads = counts_line.split()
                assert int(count) > 0, counts_line

                self.rule_count[job] += int(count)

        return fn


def run_snakemake(
    pipeline: str,
    workdir: Path,
    rules: Dict[str, int],
    config: Optional[Dict[str, Any]] = None,
    configfiles: Optional[List[Path]] = None,
    quiet: bool = True,
) -> SnakemakeLogger:
    """Runs Snakemake.

    Args:
        pipeline: the snake file to execute
        workdir: the working directory in which to run Snakemake
        rules: a mapping of rule name to expect # of times it should run
        config: the optional configuration object for Snakemake
        configfiles: the optional list of configuration files for Snakemake
        quiet: tells snakemake to not output logging, set to true for debugging failing pipelines
    """
    filename = pipeline.replace("-", "_") + ".smk"
    src_dir: Path = Path(__file__).absolute().parent.parent.parent.parent
    snakefile: Path = src_dir / "snakemake" / filename
    assert snakefile.is_file(), f"{snakefile} is not a file"

    # run it
    logger = SnakemakeLogger()
    assert snakemake.snakemake(
        snakefile=str(snakefile),
        config=config,
        configfiles=configfiles,
        resources={"mem_gb": 8},
        workdir=str(workdir),
        dryrun=True,
        quiet=quiet,
        log_handler=[logger.log_handler()],
        ignore_ambiguity=True,
    )

    # check the "all" rule
    assert (
        logger.rule_count["all"] == 1
    ), f"All rule was not run once, found: {logger.rule_count['all']}"

    # check that the executed rules were run the correct # of times
    for rule, count in logger.rule_count.items():
        assert rule in rules, f"Could not find {rule} in {rules}"
        assert count == rules[rule], f"{rule}: {rules[rule]}"

    # check that all the expected rules were run
    for rule in rules:
        assert rule in logger.rule_count

    return logger
