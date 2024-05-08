from pathlib import Path

import pytest

CONTENT = "some content"


@pytest.fixture
def example_input(tmp_path: Path) -> Path:
    example_input = tmp_path / "input.txt"
    with open(example_input, "w") as f:
        f.write(CONTENT)
    return example_input


@pytest.fixture
def example_output() -> str:
    return f"{CONTENT}\n"
