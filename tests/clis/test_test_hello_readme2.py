from pathlib import Path


def test_test_hello_readme2_file_exists():
    assert (Path(__file__).resolve().parents[1] / 'test_hello_readme2.py').is_file()
