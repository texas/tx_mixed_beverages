MANAGE=python manage.py


help:
	@echo "make commands:"
	@echo "  make help    - this help"
	@echo "  make clean   - remove temporary files"
	@echo "  make test    - run test suite"
	@echo "  make resetdb - delete and recreate the database"


clean:
	rm -rf MANIFEST
	rm -rf build
	rm -rf dist
	rm -rf *.egg-info
	find . -name "*.pyc" -delete
	find . -name ".DS_Store" -delete

# make sure to install the hstore extension in template1
test:
	ENVIRONMENT=test $(MANAGE) test


resetdb:
	-phd dropdb
	phd createdb
	phd psql -c 'CREATE EXTENSION hstore; CREATE EXTENSION postgis;'
	$(MANAGE) migrate --noinput


slurp: $(wildcard data/*.CSV)
	$(foreach file, $(wildcard data/*.CSV), \
		./mixed_beverages/scripts/slurp.py $(file);)
	echo "done"

process:
	./mixed_beverages/scripts/post_process.py

import: slurp process


# use these tasks to transfer geocoding data from one database to another
# say... between `resetdb` calls
dump_geo:
	$(MANAGE) dump_geo > geo_data.blob
load_geo:
	$(MANAGE) load_geo geo_data.blob
