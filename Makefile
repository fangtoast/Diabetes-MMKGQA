.PHONY: help bootstrap data kg up load test verify demo report package

NEO4J_URI ?= bolt://localhost:7687
NEO4J_USER ?= neo4j
NEO4J_PASSWORD ?=
NEO4J_DATABASE ?= neo4j
DATA_DIR ?= data/processed

help:
	@echo "Starter contract only; replace each placeholder as implementation lands."

bootstrap:
	@echo "TODO: install locked dependencies"

data:
	@echo "TODO: validate source manifest and build interim data"

kg:
	@python -m diabetes_mmkgqa_starter.graph_builder

up:
	@PYTHONPATH=src uvicorn diabetes_mmkgqa_starter.api.app:app --host 0.0.0.0 --port 8000 --reload

load:
	@if [ -n "$(NEO4J_PASSWORD)" ]; then \
		python -m diabetes_mmkgqa_starter.cli load --repo-root . --output-dir $(DATA_DIR) --backend neo4j --neo4j-uri $(NEO4J_URI) --neo4j-user $(NEO4J_USER) --neo4j-password $(NEO4J_PASSWORD) --neo4j-database $(NEO4J_DATABASE) --ontology-path configs/ontology.yaml ; \
	else \
		python -m diabetes_mmkgqa_starter.cli load --repo-root . --output-dir $(DATA_DIR) --backend portable --ontology-path configs/ontology.yaml ; \
	fi

test:
	@echo "TODO: run tests"

verify:
	@echo "TODO: lint + tests + data quality + smoke test"

demo:
	@echo "TODO: run fixed cases and write JSON/screenshots"

report:
	@echo "TODO: assemble report inputs or generate docx"

package:
	@echo "TODO: create final deliverable archives"
