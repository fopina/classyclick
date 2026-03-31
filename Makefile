all: lint test

sync:
	uv sync --dev --all-extras

.venv39: export VIRTUAL_ENV=.venv39
.venv39:
	uv sync --dev --all-extras --python 3.9 --active

test39: .venv39
test39: export VIRTUAL_ENV=.venv39
test39:
	uv run --active pytest --cov

.venv310: export VIRTUAL_ENV=.venv310
.venv310:
	uv sync --dev --all-extras --python 3.10 --active

test310: .venv310
test310: export VIRTUAL_ENV=.venv310
test310:
	uv run --active pytest --cov

lint:
	uv run ruff format
	uv run ruff check --fix

lint-check:
	uv run ruff format --diff
	uv run ruff check

test:
	if [ -n "$(GITHUB_RUN_ID)" ]; then \
		uv run pytest --cov --cov-report=xml --junitxml=junit.xml -o junit_family=legacy; \
	else \
		uv run python -m pytest --cov; \
	fi

testpub:
	rm -fr dist
	uv run pyproject-build
	uv run twine upload --repository testpypi dist/*

test-docs: 
	uv run mkdocs serve
