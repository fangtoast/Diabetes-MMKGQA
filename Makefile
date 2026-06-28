.PHONY: help bootstrap data kg up load test verify demo report package

NEO4J_URI ?= bolt://localhost:7687
NEO4J_USER ?= neo4j
NEO4J_PASSWORD ?=
NEO4J_DATABASE ?= neo4j
DATA_DIR ?= data/processed

help:
	@echo "Reproducible course-demo targets. On Windows, prefer scripts/run.ps1."

bootstrap:
	@python -m pip install --disable-pip-version-check -r requirements-lock.txt
	@python -m pip install -e .

data:
	@python -m diabetes_mmkgqa_starter.cli data --repo-root .

kg:
	@python -m diabetes_mmkgqa_starter.cli kg --repo-root .

up:
	@PYTHONPATH=src uvicorn diabetes_mmkgqa_starter.api.app:app --host 0.0.0.0 --port 8000 --reload

load:
	@if [ -n "$(NEO4J_PASSWORD)" ]; then \
		python -m diabetes_mmkgqa_starter.cli load --repo-root . --output-dir $(DATA_DIR) --backend neo4j --neo4j-uri $(NEO4J_URI) --neo4j-user $(NEO4J_USER) --neo4j-password $(NEO4J_PASSWORD) --neo4j-database $(NEO4J_DATABASE) --ontology-path configs/ontology.yaml ; \
	else \
		python -m diabetes_mmkgqa_starter.cli load --repo-root . --output-dir $(DATA_DIR) --backend portable --ontology-path configs/ontology.yaml ; \
	fi

test:
	@PYTHONPATH=src python -m pytest tests

verify:
	@PYTHONPATH=src python -m pytest tests

demo:
	@PYTHONPATH=src python -m diabetes_mmkgqa_starter.cli demo

report:
	@python -m diabetes_mmkgqa_starter.cli report --repo-root .

package:
	@mkdir -p deliverables
	@python -m diabetes_mmkgqa_starter.cli package --repo-root . --package-output-dir deliverables --package-name diabetes_mmkgqa_deliverables.zip
