from pathlib import Path

from .readme_tester import ReadmeParsingTestCase


class TestReadme(ReadmeParsingTestCase):
    README_PATH = Path(__file__).resolve().parents[1] / 'README.md'
    TESTS_DIR = Path(__file__).resolve().parent
