from pathlib import Path


def test_cli_click_file_exists():
    assert (Path(__file__).resolve().parents[1] / 'cli_click.py').is_file()
