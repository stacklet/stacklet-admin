install:
  poetry install
  poetry run python setup.py develop
  poetry run pre-commit install

test:
  poetry run pytest --cov=stacklet_cli tests
