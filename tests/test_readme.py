from pathlib import Path

from readme_example_tester import ReadmeTestCase


class TestReadme(ReadmeTestCase):
    README_PATH = Path(__file__).resolve().parents[1] / 'README.md'
    TESTS_DIR = Path(__file__).resolve().parent
