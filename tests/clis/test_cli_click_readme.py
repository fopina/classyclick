from pathlib import Path


def test_cli_click_readme_file_exists():
    assert (Path(__file__).resolve().parents[1] / 'cli_click_readme.py').is_file()
