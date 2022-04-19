"""Tests for the hello-world pipeline"""


from typing import Dict

from py._path.local import LocalPath as TmpDir
from pyclient.tests.util import run_snakemake


def test_hello_world(tmpdir: TmpDir) -> None:
    """Basic unit test that runs the snakefile in dry-run mode to ensure it
    parses correctly.
    """

    rules: Dict[str, int] = {
        "all": 1,
        "hello_world": 1,
    }

    run_snakemake(pipeline="hello-world", workdir=tmpdir, rules=rules)
