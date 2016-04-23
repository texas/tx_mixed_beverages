MANAGE=python manage.py

help: ## Shows this help
	@echo "$$(grep -h '#\{2\}' $(MAKEFILE_LIST) | sed 's/: #\{2\} /	/' | column -t -s '	')"

install: ## Install requirements
	pip install -r requirements.txt
	npm install

requirements.txt: ## Generate a new requirements.txt
requirements.txt: requirements.in
	pip-compile $< > $@

clean: ## Remove temporary files
	rm -rf MANIFEST
	rm -rf build
	rm -rf dist
	rm -rf *.egg-info
	find . -name "*.pyc" -delete
	find . -name ".DS_Store" -delete

# Note: make sure to install the hstore extension in template1
test: ## Run test suite
	$(MANAGE) test

resetdb: ## Delete and recreate the database
	-phd dropdb
	phd createdb
	phd psql -c 'CREATE EXTENSION hstore; CREATE EXTENSION postgis;'
	$(MANAGE) migrate --noinput

.PHONY: data/*.CSV
data/*.CSV:
	./mixed_beverages/scripts/slurp.py $@

slurp: ## Import all csvs found in ./data
slurp: data/*.CSV

process: ## Generate stats
	./mixed_beverages/scripts/post_process.py

import: ## Shortcut for 'make slurp process'
import: slurp process


# use these tasks to transfer geocoding data from one database to another
# say... between `resetdb` calls
dump_geo:
	$(MANAGE) dump_geo > data/geo_data.blob
load_geo:
	$(MANAGE) load_geo data/geo_data.blob


docker/build:
	docker build -t crccheck/mixed_beverages .

docker/run:
	docker run --rm -p 8080:8080 crccheck/mixed_beverages
