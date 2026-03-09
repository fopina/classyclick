from pathlib import Path


def test_cli_next_ctx_meta_file_exists():
    assert (Path(__file__).resolve().parents[1] / 'cli_next_ctx_meta.py').is_file()
