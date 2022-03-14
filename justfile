pkg_domain := "stacklet"
pkg_repo := "platform-cli"
pkg_owner := "532725030595"
pkg_region := "us-east-1"

default:
	@just --list

install:
	poetry install
	poetry run pre-commit install

test *flags:
	poetry run pytest --cov=stacklet tests {{ flags }}

pkg-login:
	#!/bin/bash
	export AWS_DEFAULT_REGION={{pkg_region}}
	aws codeartifact login --tool pip --domain {{pkg_domain}} \
	         --domain-owner {{pkg_owner}} --repository {{pkg_repo}}
	aws codeartifact login --tool twine --domain {{pkg_domain}} \
	         --domain-owner {{pkg_owner}} --repository {{pkg_repo}}

	export CODEARTIFACT_REPOSITORY_URL=`aws codeartifact get-repository-endpoint --domain {{pkg_domain}} --domain-owner {{pkg_owner}} --repository {{pkg_repo}} --format pypi --query repositoryEndpoint --output text`
	export CODEARTIFACT_AUTH_TOKEN=`aws codeartifact get-authorization-token --domain {{pkg_domain}} --domain-owner {{pkg_owner}} --query authorizationToken --output text`
	export CODEARTIFACT_USER=aws

	# Now use all of these when configuring the repo in poetry
	echo $CODEARTIFACT_REPOSITORY_URL
	poetry config repositories.{{pkg_repo}} $CODEARTIFACT_REPOSITORY_URL
	poetry config http-basic.{{pkg_repo}} $CODEARTIFACT_USER $CODEARTIFACT_AUTH_TOKEN

pkg-publish:
	rm -f dist/*
	poetry publish -vvv --build -r {{pkg_repo}}

compile: install
	poetry run python -m nuitka stacklet/client/platform/cli.py -o stacklet-admin --standalone --onefile --assume-yes-for-downloads --include-package-data=* --remove-output --static-libpython=no
	chmod +x stacklet-admin
	export PATH=$PWD/:$PATH
