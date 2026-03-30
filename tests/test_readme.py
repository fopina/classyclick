from pathlib import Path

from readme_example_tester import ReadmeTestCase


class TestReadme(ReadmeTestCase):
    README_PATH = Path(__file__).resolve().parents[1] / 'README.md'
    TESTS_DIR = Path(__file__).resolve().parent

    def _expected_clis_test_path(self, cli_target: str):
        target = self._normalize_cli_target(cli_target)
        target_stem = Path(target).with_suffix('').name
        if target_stem.startswith('test_'):
            return None
        return self.TESTS_DIR / 'clis' / f'test_{target_stem}.py'
