.PHONY: deps build test validate generate-data ground-truth

deps:
	dbt deps

build:
	dbt build

test:
	dbt test

validate:
	python scripts/validate.py

generate-data:
	python scripts/generate_source_data.py

ground-truth:
	python scripts/compute_ground_truth.py --write
