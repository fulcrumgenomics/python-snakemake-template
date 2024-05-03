from pathlib import Path

from toolkit.tools import example


def test_example(tmp_path: Path, example_input: Path, example_output: str) -> None:
    outfile = tmp_path / "output.txt"
    example.example(input_file=example_input, output_file=outfile)
    with open(outfile) as f:
        assert f.read() == example_output
