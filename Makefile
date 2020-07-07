MANAGE=python manage.py

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

# TODO use the json api to do incremental updates
# Sort because it's too large for csvsort. Takes 53s but saves 6 hours to import
slurp: ## Import downloaded CSVs
	wget 'https://data.texas.gov/api/views/naix-2893/rows.csv?accessType=DOWNLOAD&api_foundry=true' -O data/Mixed_Beverage_Gross_Receipts.csv
	(head -n 1 data/Mixed_Beverage_Gross_Receipts.csv && tail -n +2 data/Mixed_Beverage_Gross_Receipts.csv | sort) > data/Mixed_Beverage_Gross_Receipts_sorted.csv
	$(MANAGE) slurp data/Mixed_Beverage_Gross_Receipts_sorted.csv
	$(MANAGE) post_process

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
