.PHONY: help bootstrap data kg up load test verify demo report package

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
	@echo "TODO: idempotent Neo4j import"

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
