from pathlib import Path


def test_cli_hello_simple_file_exists():
    assert (Path(__file__).resolve().parents[1] / 'cli_hello_simple.py').is_file()
