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
README_BLOCK_START_RE = re.compile(r'^\s*#\s*README\s*\+\+\+\s*$')
README_BLOCK_END_RE = re.compile(r'^\s*#\s*README\s*---\s*$')


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


def _cli_file_is_excluded(cli_file: Path) -> bool:
    return any(README_EXCLUDE_RE.match(line) for line in cli_file.read_text(encoding='utf-8').splitlines())


def _readme_expected_cli_blocks(cli_file: Path) -> list[str]:
    lines = cli_file.read_text(encoding='utf-8').splitlines()
    blocks: list[str] = []
    collecting = False
    block: list[str] = []

    for line in lines:
        if README_BLOCK_START_RE.match(line):
            if collecting:
                raise ValueError(f'Nested README marker in {cli_file}')
            collecting = True
            block = []
            continue

        if README_BLOCK_END_RE.match(line):
            if not collecting:
                raise ValueError(f'Unexpected README end marker in {cli_file}')
            blocks.append('\n'.join(block).rstrip())
            collecting = False
            continue

        if collecting:
            block.append(line)

    if collecting:
        raise ValueError(f'Unclosed README marker in {cli_file}')

    if blocks:
        return blocks

    return [cli_file.read_text(encoding='utf-8').rstrip()]


class TestReadme(unittest.TestCase):
    def test_readme_cli_code_blocks_match_tests(self):
        readme_entries = list(_iter_readme_examples())
        expected_marker_targets = set()
        used_blocks_per_cli: dict[str, int] = {}

        for example in readme_entries:
            with self.subTest(example_line=example.line, cli=example.cli):
                target = _normalize_cli_target(example.cli)
                cli_file = TESTS_DIR / target
                self.assertTrue(
                    cli_file.exists(),
                    f'README marker at line {example.line} points to {example.cli}, but {cli_file} does not exist',
                )

                if _cli_file_is_excluded(cli_file):
                    continue

                expected_marker_targets.add(target)

                if example.language != 'python':
                    continue

                cli_blocks = _readme_expected_cli_blocks(cli_file)
                used = used_blocks_per_cli.get(target, 0)
                self.assertLess(
                    used,
                    len(cli_blocks),
                    (
                        f'README example at line {example.line} points to {example.cli} '
                        f"but it has no matching README block between '# README +++' markers"
                    ),
                )

                self.assertEqual(
                    example.code,
                    cli_blocks[used],
                    f'README example at line {example.line} does not match {cli_file} block {used + 1}.',
                )

                used_blocks_per_cli[target] = used + 1
