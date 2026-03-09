from pathlib import Path


def test_cli_next_ctx_obj_file_exists():
    assert (Path(__file__).resolve().parents[1] / 'cli_next_ctx_obj.py').is_file()
