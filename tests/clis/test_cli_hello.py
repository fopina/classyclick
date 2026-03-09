from pathlib import Path


def test_cli_hello_file_exists():
    assert (Path(__file__).resolve().parents[1] / 'cli_hello.py').is_file()
