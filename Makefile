MANAGE=poetry run python manage.py

help: ## Shows this help
	@echo "$$(grep -h '#\{2\}' $(MAKEFILE_LIST) | sed 's/: #\{2\} /	/' | column -t -s '	')"

install: ## Install requirements
	poetry install
	npm install

clean: ## Remove temporary files
	rm -rf MANIFEST
	rm -rf build
	rm -rf dist
	rm -rf *.egg-info
	find . -name "*.pyc" -delete
	find . -name ".DS_Store" -delete

# Note: make sure to install the hstore extension in template1
test: ## Run test suite
	$(MANAGE) test --noinput

tdd: ## Run tests with a watcher
	nodemon --ext py -x sh -c "$(MANAGE) test --failfast --keepdb || true"

lint: ## Run lint check
	black --check .

resetmigrations:
	find . -name "0001_initial.py" -delete
	$(MANAGE) makemigrations receipts lazy_geo
	black .

resetdb: ## Delete and recreate the database
	-phd dropdb
	phd createdb
	phd psql -c 'CREATE EXTENSION postgis;'
	$(MANAGE) migrate --noinput

# WIP
install/geocode:
	phd psql -c 'CREATE EXTENSION fuzzystrmatch; CREATE EXTENSION postgis_tiger_geocoder; CREATE EXTENSION postgis_topology;'

admin: ## Set up a local admin/admin account
	echo "from django.contrib.auth import get_user_model; \
	  User = get_user_model(); \
	  User.objects.create_superuser('admin', 'admin@example.com', 'admin')" | \
	  python manage.py shell

.PHONY: data
data:
	wget 'https://data.texas.gov/api/views/naix-2893/rows.csv?accessType=DOWNLOAD&api_foundry=true' -O data/Mixed_Beverage_Gross_Receipts.csv
	(head -n 1 data/Mixed_Beverage_Gross_Receipts.csv && tail -n +2 data/Mixed_Beverage_Gross_Receipts.csv | sort) > data/Mixed_Beverage_Gross_Receipts_sorted.csv

# TODO use the json api to do incremental updates
# Sort because it's too large for csvsort. Takes 53s but saves 6 hours to import
# Takes 25m to run from scratch
slurp: ## Import downloaded CSVs
	$(MANAGE) slurp data/Mixed_Beverage_Gross_Receipts_sorted.csv

# Takes 1h34m to run from scratch
process: ## Generate stats
	$(MANAGE) post_process

import: ## Shortcut for 'make data slurp process'
import: data slurp process


# use these tasks to transfer geocoding data from one database to another
# say... between `resetdb` calls
dump_geo:
	$(MANAGE) dump_geo > data/geo_data.jsonl
load_geo:
	$(MANAGE) load_geo data/geo_data.jsonl


docker/build:
	docker build -t crccheck/mixed_beverages .

docker/run:
	docker run --rm -p 8080:8080 crccheck/mixed_beverages

site: ## Create a static site version of the app
	npm run build
	mkdir -p _site
	cd _site && wget -r localhost:8000 --force-html -e robots=off -nH -nv --max-redirect 0 || true
	$(MANAGE) site --overwrite
