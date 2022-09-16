pkg_domain := "stacklet"
pkg_repo := "stacklet.client.platform"
# customer delivery
pkg_owner := "653993915282"
pkg_region := "us-east-1"

default:
	@just --list

install:
	poetry install
	poetry run pre-commit install

test *flags:
	poetry run pytest --cov=stacklet tests {{ flags }}

# login to private package repository and configure tools
pkg-login:
	#!/usr/bin/env bash
	set -euo pipefail

	# codebuild is setting this one
	export AWS_REGION={{pkg_region}}
	# humans typically set this one
	export AWS_DEFAULT_REGION={{pkg_region}}

	aws codeartifact login --tool twine --domain {{pkg_domain}} \
		--domain-owner {{pkg_owner}} --repository {{pkg_repo}}

	export CODEARTIFACT_REPOSITORY_URL=`aws codeartifact get-repository-endpoint --domain {{pkg_domain}} --domain-owner {{pkg_owner}} --repository {{pkg_repo}} --format pypi --query repositoryEndpoint --output text`
	export CODEARTIFACT_AUTH_TOKEN=`aws codeartifact get-authorization-token --domain {{pkg_domain}} --domain-owner {{pkg_owner}} --query authorizationToken --output text`
	export CODEARTIFACT_USER=aws

	# Now use all of these when configuring the repo in poetry
	echo -e "CODEARTIFACT_REPOSITORY_URL=$CODEARTIFACT_REPOSITORY_URL\nCODEARTIFACT_AUTH_TOKEN=$CODEARTIFACT_AUTH_TOKEN\nCODEARTIFACT_USER=$CODEARTIFACT_USER\n" > pkg-build.secret
	poetry config repositories.{{pkg_repo}} $CODEARTIFACT_REPOSITORY_URL
	poetry config http-basic.{{pkg_repo}} $CODEARTIFACT_USER $CODEARTIFACT_AUTH_TOKEN


	# ...and pip for good measure
	#
	# Note: `aws codeartifact login --tool pip` updates user-level pip settings. As a finer-grained alternative, we can
	# build a PyPI index URL and use it only inside our virtual environment.
	export PYPI_INDEX_URL="https://${CODEARTIFACT_USER}:${CODEARTIFACT_AUTH_TOKEN}@${CODEARTIFACT_REPOSITORY_URL#*//}simple/"
	poetry run python -m pip config --site set global.index-url "$PYPI_INDEX_URL"

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

# publish package to private pypi repository
pkg-publish:
	#!/usr/bin/env bash
	set -e
	rm -f dist/*
	if poetry run python scripts/upgrade.py check-publish; then
		echo "publishing..."
		poetry publish -vvv --build -r {{pkg_repo}}
	else
		echo "skipping publish"
	fi
