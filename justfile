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

compile: install
    uv run python -m nuitka stacklet/client/platform/cli.py -o stacklet-admin --standalone --onefile --assume-yes-for-downloads --include-package-data=* --remove-output --static-libpython=no
    chmod +x stacklet-admin
    export PATH=$PWD/:$PATH

pkg-prep bump="--bump-patch":
    uv run python scripts/upgrade.py upgrade {{bump}}
    uv lock --upgrade
    git add justfile pyproject.toml uv.lock
    git status
