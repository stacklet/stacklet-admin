install:
  poetry install
  poetry run python setup.py develop

test:
  poetry run pytest --cov=cli tests
