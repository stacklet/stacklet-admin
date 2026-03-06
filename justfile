default:
    @just --list

install:
    uv sync
    uv run pre-commit install

lint:
    uv run ruff check
    uv run ruff format --check
    uv run deptry .

format:
    uv run ruff format
    uv run ruff check --fix

test *flags:
    uv run pytest --cov=stacklet tests {{ flags }}

pkg-prep version="":
    uv run python scripts/upgrade.py {{version}}
    uv lock --upgrade
    git add stacklet/client/platform/__init__.py uv.lock
    git status
