from pathlib import Path


def test_cli_bye_file_exists():
    assert (Path(__file__).resolve().parents[1] / 'cli_bye.py').is_file()
