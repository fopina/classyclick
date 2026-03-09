from pathlib import Path


def test_cli_short_samples_file_exists():
    assert (Path(__file__).resolve().parents[1] / 'cli_short_samples.py').is_file()
