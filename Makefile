COMPOSE_RUN_BASE = docker compose run --rm base
COMPOSE_RUN_PYTHON = docker compose run --rm python
SHELL := $(shell which bash)
.SECONDEXPANSION:

createTransformationDag: dockerDeps
	$(COMPOSE_RUN_PYTHON) make _template.testapi

_template.create_ingestion_dag: _pythonDeps
	poetry run python template/testapi/create.py

createIngestionPr:
	gh pr create --body-file template/testapi/PULL_REQUEST_TEMPLATE.md --fill


dockerDeps: envFile

dockerBuild.%:
	@echo "::group::Docker Build $*"
	docker compose build $*
	@echo "::endgroup::"

_pythonDeps:
	@echo "::group::Install Python Dependencies"
	poetry install
	@echo "::endgroup::"

pythonLint: envFile dockerDeps dockerBuild.python
	$(COMPOSE_RUN_PYTHON) make _pythonLint

_pythonLint: _pythonDeps
	poetry run autoflake .
	poetry run black .

clean: envFile cleanDocker

cleanDocker:
	docker compose down --remove-orphans --volumes

pruneDocker:
	docker compose down --remove-orphans



# The CI variable (used below) is defined by GitHub actions, so this step will only be used in that environment.
ifndef CI
ciEnv:
else
ciEnv:
	cat .env.ci >> .env
endif

localEnv:
	cat .env.local >> .env

envFile: localEnv
	$(eval include .env)
	$(eval export)
