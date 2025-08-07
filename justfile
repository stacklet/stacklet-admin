default:
	@just --list

install:
	poetry install
	poetry run pre-commit install

lint:
  poetry run ruff check
  poetry run ruff format --check
  poetry run deptry .

format:
  poetry run ruff format
  poetry run ruff check --fix

test *flags:
	poetry run pytest --cov=stacklet tests {{ flags }}

compile: install
	poetry run python -m nuitka stacklet/client/platform/cli.py -o stacklet-admin --standalone --onefile --assume-yes-for-downloads --include-package-data=* --remove-output --static-libpython=no
	chmod +x stacklet-admin
	export PATH=$PWD/:$PATH

pkg-prep bump="--bump-patch":
	poetry run python scripts/upgrade.py upgrade {{bump}}
	poetry update
	poetry lock
	git add justfile pyproject.toml poetry.lock
	git status
