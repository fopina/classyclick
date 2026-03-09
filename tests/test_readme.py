from dataclasses import dataclass
from pathlib import Path
from typing import Optional
import re
import shlex
import subprocess
import sys
import unittest


README_PATH = Path(__file__).resolve().parents[1] / 'README.md'
TESTS_DIR = Path(__file__).resolve().parent

EXAMPLE_RE = re.compile(
    r"(?ms)^[ \t]*<!--\s*(?P<kind>example-id(?:-output)?)\s*:\s*(?P<marker>.+?)\s*-->\s*```(?P<lang>\S*)\s*\n(?P<code>.*?)```"
)
README_EXCLUDE_RE = re.compile(r"^\s*#\s*README-EXCLUDE\b")
README_BLOCK_START_RE = re.compile(r"^\s*#\s*README(?::(?P<block_id>\S+))?\s*\+\+\+\s*$")
README_BLOCK_END_RE = re.compile(r"^\s*#\s*README(?::(?P<block_id>\S+))?\s*---\s*$")


@dataclass
class ReadmeExample:
    line: int
    cli: str
    readme_id: Optional[str]
    args: list[str]
    language: str
    code: str
    is_output: bool


def _normalize_cli_target(cli_target: str) -> str:
    normalized = cli_target.strip().removeprefix('tests/')
    return normalized if normalized.endswith('.py') else f"{normalized}.py"


def _split_cli_target(cli_target: str) -> tuple[str, Optional[str]]:
    cli_file, separator, readme_id = cli_target.partition(':')
    if not separator:
        return cli_file, None
    return cli_file, readme_id


def _iter_readme_examples():
    readme = README_PATH.read_text()

    for match in EXAMPLE_RE.finditer(readme):
        raw_marker = match.group('marker').strip()
        marker_parts = shlex.split(raw_marker)
        if not marker_parts:
            line = readme[:match.start()].count('\n') + 1
            raise ValueError(f"Empty example-id found at line {line} in README")

        cli_target, readme_id = _split_cli_target(marker_parts[0])
        cli_args = marker_parts[1:]

        yield ReadmeExample(
            line=readme[:match.start()].count('\n') + 1,
            cli=cli_target,
            readme_id=readme_id,
            args=cli_args,
            language=match.group('lang'),
            code=match.group('code').rstrip(),
            is_output=match.group('kind') == 'example-id-output',
        )


def _cli_file_is_excluded(cli_file: Path) -> bool:
    return any(
        README_EXCLUDE_RE.match(line)
        for line in cli_file.read_text(encoding='utf-8').splitlines()
    )


def _readme_blocks_in_cli_file(cli_file: Path) -> dict[Optional[str], list[str]]:
    lines = cli_file.read_text(encoding='utf-8').splitlines()
    blocks: dict[Optional[str], list[str]] = {}
    current_id: Optional[str] = None
    collecting = False
    block: list[str] = []
    has_markers = False

    for line in lines:
        start_match = README_BLOCK_START_RE.match(line)
        if start_match:
            if collecting:
                raise ValueError(f"Nested README marker in {cli_file}")
            collecting = True
            has_markers = True
            current_id = start_match.group('block_id')
            block = []
            continue

        end_match = README_BLOCK_END_RE.match(line)
        if end_match:
            if not collecting:
                raise ValueError(f"Unexpected README end marker in {cli_file}")
            end_id = end_match.group('block_id')
            if end_id is not None and current_id is not None and end_id != current_id:
                raise ValueError(f"README end marker id mismatch in {cli_file}")
            blocks.setdefault(current_id, []).append('\n'.join(block).rstrip())
            collecting = False
            current_id = None
            continue

        if collecting:
            block.append(line)

    if collecting:
        raise ValueError(f"Unclosed README marker in {cli_file}")

    return blocks if has_markers else {}


def _readme_expected_cli_blocks(cli_file: Path, readme_id: Optional[str]) -> list[str]:
    blocks = _readme_blocks_in_cli_file(cli_file)

    if not blocks:
        if readme_id is not None:
            return []
        return [cli_file.read_text(encoding='utf-8').rstrip()]

    return blocks.get(readme_id, [])


def _cli_file_block_groups(cli_file: Path) -> dict[Optional[str], list[str]]:
    blocks = _readme_blocks_in_cli_file(cli_file)
    if blocks:
        return blocks
    return {None: [cli_file.read_text(encoding='utf-8').rstrip()]}


def _normalize_output(output: str) -> str:
    lines = output.rstrip().splitlines()
    while lines and lines[0].lstrip().startswith('$'):
        lines = lines[1:]
    return '\n'.join(lines).rstrip()


def _run_cli_output(cli_target: str, args: list[str]) -> str:
    cmd = [cli_target, *args]

    result = subprocess.run(
        cmd,
        cwd=TESTS_DIR.parent,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    if result.returncode != 0:
        raise AssertionError(f"Command failed: {' '.join(cmd)}\nOutput:\n{result.stdout}")
    return _normalize_output(result.stdout)


class TestReadme(unittest.TestCase):
    def test_readme_cli_code_blocks_match_tests(self):
        self.maxDiff = None
        readme_entries = list(_iter_readme_examples())
        expected_marker_targets = set()
        used_blocks_per_cli: dict[str, dict[Optional[str], int]] = {}
        self.assertEqual(len(readme_entries), 20)

        for example in readme_entries:
            with self.subTest(
                example_line=example.line,
                cli=example.cli,
                readme_id=example.readme_id,
                kind='output' if example.is_output else 'code',
            ):
                target = _normalize_cli_target(example.cli)
                cli_file = TESTS_DIR / target
                self.assertTrue(
                    cli_file.exists(),
                    f"README marker at line {example.line} points to {example.cli}, "
                    f"but {cli_file} does not exist",
                )
                if _cli_file_is_excluded(cli_file):
                    continue

                if example.is_output:
                    expected_output = _normalize_output(example.code)
                    self.assertEqual(
                        _run_cli_output(example.cli, example.args),
                        expected_output,
                        f"README output example at line {example.line} does not match output of {example.cli}.",
                    )
                    continue

                expected_marker_targets.add(target)

                cli_blocks = _readme_expected_cli_blocks(cli_file, example.readme_id)
                self.assertTrue(
                    bool(cli_blocks),
                    (
                        f"README example at line {example.line} points to {example.cli} "
                        f"but there is no README block with id {example.readme_id!r}."
                    ),
                )

                used = used_blocks_per_cli.setdefault(target, {}).get(example.readme_id, 0)
                self.assertLess(
                    used,
                    len(cli_blocks),
                    (
                        f"README example at line {example.line} points to {example.cli} "
                        f"but it has more references than available README blocks for id {example.readme_id!r}."
                    ),
                )

                cli_code = cli_blocks[used]
                example_code = example.code.rstrip()

                if example.language == 'python':
                    self.assertEqual(
                        example_code,
                        cli_code,
                        (
                            f"README example at line {example.line} does not match {cli_file} "
                            f"block id={example.readme_id!r}."
                        ),
                    )

                used_blocks_per_cli[target][example.readme_id] = used + 1

        for cli_file in sorted(TESTS_DIR.glob('cli*.py')):
            if _cli_file_is_excluded(cli_file):
                continue

            target = cli_file.name
            file_block_groups = _cli_file_block_groups(cli_file)
            if len(file_block_groups) == 1 and file_block_groups.get(None) is not None:
                continue
            if target not in expected_marker_targets:
                self.fail(f"{target} has no README example marker")

            used = used_blocks_per_cli.get(target, {})
            for block_id, block_values in file_block_groups.items():
                with self.subTest(cli=target, readme_id=block_id, scope='block_coverage'):
                    self.assertEqual(
                        used.get(block_id, 0),
                        len(block_values),
                        f"README is missing or has too many references for {target} id={block_id!r}",
                    )
