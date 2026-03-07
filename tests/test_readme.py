import re
import shlex
import unittest
from dataclasses import dataclass
from pathlib import Path

README_PATH = Path(__file__).resolve().parents[1] / 'README.md'
TESTS_DIR = Path(__file__).resolve().parent

EXAMPLE_RE = re.compile(
    r'(?ms)^[ \t]*<!--\s*example-id:\s*(?P<marker>.+?)\s*-->\s*```(?P<lang>\S*)\s*\n(?P<code>.*?)```'
)
README_EXCLUDE_RE = re.compile(r'^\s*#\s*README-EXCLUDE\b')


@dataclass
class ReadmeExample:
    line: int
    cli: str
    args: list[str]
    language: str
    code: str


def _normalize_cli_target(cli_target: str) -> str:
    normalized = cli_target.strip().removeprefix('tests/')
    return normalized if normalized.endswith('.py') else f'{normalized}.py'


def _cli_file_is_excluded(cli_file: Path) -> bool:
    return any(README_EXCLUDE_RE.match(line) for line in cli_file.read_text(encoding='utf-8').splitlines())


def _iter_readme_examples():
    readme = README_PATH.read_text()

    for match in EXAMPLE_RE.finditer(readme):
        raw_marker = match.group('marker').strip()
        marker_parts = shlex.split(raw_marker)
        if not marker_parts:
            line = readme[: match.start()].count('\n') + 1
            raise ValueError(f'Empty example-id found at line {line} in README')
        cli_target = marker_parts[0]
        cli_args = marker_parts[1:]

        yield ReadmeExample(
            line=readme[: match.start()].count('\n') + 1,
            cli=cli_target,
            args=cli_args,
            language=match.group('lang'),
            code=match.group('code').rstrip(),
        )


class TestReadme(unittest.TestCase):
    def test_readme_cli_code_blocks_match_tests(self):
        readme_entries = list(_iter_readme_examples())
        expected_marker_targets = set()
        self.assertEqual(len(readme_entries), 19)

        for example in readme_entries:
            with self.subTest(example_line=example.line, cli=example.cli):
                target = _normalize_cli_target(example.cli)
                expected_marker_targets.add(target)

                cli_file = TESTS_DIR / target
                self.assertTrue(
                    cli_file.exists(),
                    f'README marker at line {example.line} points to {example.cli}, but {cli_file} does not exist',
                )
                if _cli_file_is_excluded(cli_file):
                    continue

                if example.language != 'python':
                    continue

                cli_code = cli_file.read_text().rstrip()
                example_code = example.code.rstrip()

                self.assertEqual(
                    example_code,
                    cli_code,
                    f'README example at line {example.line} does not match {cli_file}.',
                )
