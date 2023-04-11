"""Testing utilities for :module:`~pyclient.tools`"""

import pytest


def _to_name(tool) -> str:  # type: ignore
    """Gives the tool name for a function by taking the function name and replacing
    underscores with hyphens."""
    return tool.__name__.replace("_", "-")


def test_tool_funcs(tool, main) -> None:  # type: ignore
    name = _to_name(tool)
    argv = [name, "-h"]
    with pytest.raises(SystemExit) as e:
        main(argv=argv)
    assert e.type == SystemExit
    assert e.value.code == 0  # code should be 0 for help
