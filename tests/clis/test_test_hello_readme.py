from pathlib import Path


def test_test_hello_readme_file_exists():
    assert (Path(__file__).resolve().parents[1] / 'test_hello_readme.py').is_file()
