################################################################################
# Hello World pipeline
################################################################################

from pathlib import Path
from typing import List

from pyclient.pipeline import snakemake_utils


################################################################################
# Utility methods and variables
################################################################################

# TODO

################################################################################
# Terminal files
################################################################################

all_terminal_files: List[Path] = [Path("message.txt")]

################################################################################
# Snakemake rules
################################################################################

onerror:
    """Block of code that gets called if the snakemake pipeline exits with an error."""
    snakemake_utils.on_error(snakefile=Path(__file__), config=config, log=Path(log))


rule all:
    input:
        all_terminal_files

rule hello_world:
    output:
        txt = "message.txt"
    log:
        "logs/hello_world.log"
    benchmark:
        "benchmarks/hello_world.txt"
    shell:
        "(echo Hello World > {output.txt}) &> {log}"
