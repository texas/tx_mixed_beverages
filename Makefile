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


test:
	ENVIRONMENT=test $(MANAGE) test


resetdb:
	-phd dropdb
	phd createdb
	$(MANAGE) migrate --noinput


slurp: $(wildcard data/*.CSV)
	$(foreach file, $(wildcard data/*.CSV), \
		./mixed_beverages/scripts/slurp.py $(file);)
	echo "done"

process:
	./mixed_beverages/scripts/post_process.py

import: slurp process
