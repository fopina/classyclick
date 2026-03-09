# AGENTS for /Users/fopina/Documents/classyclick

## Project context

`classyclick` is a small Python package that wraps `click` CLI definitions in dataclass-like classes.

- `classyclick/command.py` contains the `@classyclick.command()` decorator and click command wiring.
- `classyclick/fields.py` defines `Option`, `Argument`, and context helpers.
- `classyclick/utils.py` has string conversion helpers used for parameter naming.
- `tests/` contains behavior coverage for CLI execution, defaults, inheritance, and edge cases.
- `README.md` is the canonical usage reference.
- `.github/workflows/` contains CI and publish/release pipelines.

## Environment and setup

- Python project with `pyproject.toml`; development uses `uv`.
- Set up dependencies with `uv sync --dev`.
- Supported runtime targets include Python 3.9+ (CI currently exercises 3.9, 3.12, and 3.13).

## Development commands

- `make lint` — run formatter + auto-fixes (`ruff format`, `ruff check --fix`).
- `make lint-check` — strict lint check (no fixes).
- `make test` — run pytest with coverage.
  - In CI (`GITHUB_RUN_ID` set), outputs `coverage.xml` and `junit.xml`.
- `uv run pyproject-build` — build artifacts.
- `uv run twine upload ...` — used by publish workflows only.

## Style and conventions

- Follow existing style and let `ruff format` format files.
- Use single quotes unless escaped content requires otherwise.
- Keep max line length at 120.
- Prefer small, explicit changes in `classyclick/`.
- Maintain test coverage for behavior changes under `tests/`.
- Avoid editing generated or ephemeral directories/files:
  - `.coverage`, `dist/`, `.venv/`, `.pytest_cache/`, `.ruff_cache/`, `.tox/`, coverage artifacts, etc.

## Testing expectations

- Test framework: `pytest` with `unittest.TestCase` patterns.
- Always write new tests using `unittest.TestCase` / `tests.BaseCase`; avoid bare pytest-style test functions.
- CLI behavior is typically validated with `click.testing.CliRunner` through `*.click`.
- Add tests for behavior changes and regressions (especially around default/required inference and click-version-sensitive behavior).
- Keep click-version compatibility in mind (`click==7.0` and `click > 8` are explicitly exercised in CI).

## Release and versioning

- Version lives in `classyclick/__version__.py`.
- `.github/change_version.py --set <version>` updates the version string.
- Publishing uses `.github/workflows/publish.yml` and `publish-main.yml`/`publish-dev.yml`.

## Practical guidance for edits

- Touch only what is needed; this is a compact codebase.
- Preserve public API behavior unless intentionally changing it.
- If changing field/command behavior, verify/update tests that document edge cases in command arguments/options/context injection.
