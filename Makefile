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
	@echo "TODO: docker compose up -d"

load:
	@python -m diabetes_mmkgqa_starter.db.neo4j_loader \
		--repo-root . \
		--output-dir $(DATA_DIR) \
		--uri $(NEO4J_URI) \
		--user $(NEO4J_USER) \
		--database $(NEO4J_DATABASE) \
		--ontology-path configs/ontology.yaml \
		$(if $(NEO4J_PASSWORD),--password $(NEO4J_PASSWORD),--dry-run)

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
