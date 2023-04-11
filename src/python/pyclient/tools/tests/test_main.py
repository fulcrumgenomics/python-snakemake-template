"""Tests for :module:`~pyclient.tools.__main__
Motivation
~~~~~~~~~~
The idea is to run help on the main tools method (`-h`) as well as on
each tool (ex. `tool-name -h`).  This should force :module:`~defopt`
to parse the docstring for the method.  Since :module:`~defopt` uses
:module:`~argparse` underneath, `SystemExit`s are raised, which are
different than regular `Exceptions`.  The exit code returned by help
(the usage) is 0.  An improperly formatted docstring throws a
:class:`NotImplementedException`.  We add a few tests below to show
this.
"""

import pytest
from pyclient.tools.__main__ import TOOLS
from pyclient.tools.__main__ import main
from pyclient.tools.tests import test_tool_funcs as _test_tool_funcs


def test_tools_help() -> None:
    """Tests that running pyclient-tools with -h exits OK"""
    argv = ["-h"]
    with pytest.raises(SystemExit) as e:
        main(argv=argv)
    assert e.type == SystemExit
    assert e.value.code == 0  # code should be 0 for help


@pytest.mark.parametrize("tool", TOOLS)
def test_tool_funcs(tool) -> None:  # type: ignore
    _test_tool_funcs(tool, main)
