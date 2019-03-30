VERSION=2.0.0
BUILDDIR='~build'
PYTHONPATH:=${PWD}/tests/:${PWD}:${PYTHONPATH}
SUBDIRS:=$(wildcard plugins/bitcaster-*)
BITCASTER_DATABASE_HOST?=127.0.0.1
BITCASTER_DATABASE_PORT?=5432
BUILDDIR?=./~build

.mkbuilddir:
	@mkdir -p ${BUILDDIR}

help:
	@echo "develop                 setup development environment"
	@echo "lint                    lint source code"
	@echo "clean                   clean dev environment"
	@echo "fullclean               totally remove any development related files"
	@echo "static                  run webpack to compile static files"
	@echo "messages                create translations files"
	@echo ""
	@echo "DANGEROUS COMMANDS"
	@echo "reset-migrations        reset all database migrations"
	@echo ""



static:
	node_modules/.bin/webpack --mode development
	bitcaster upgrade --no-migrate --no-input

develop:
	git config branch.autosetuprebase always
	@pipenv install --ignore-pipfile --dev
	pipenv run pre-commit install
	pipenv run pre-commit install --hook-type pre-push
	$(MAKE) .init-db
	pip install -e .

.init-db:
	# initializing '${DBENGINE}' database 'bitcaster'
	psql -h ${BITCASTER_DATABASE_HOST} -p ${BITCASTER_DATABASE_PORT} -U postgres -c "DROP DATABASE IF EXISTS test_bitcaster"
	psql -h ${BITCASTER_DATABASE_HOST} -p ${BITCASTER_DATABASE_PORT} -U postgres -c "DROP DATABASE IF EXISTS bitcaster"
	psql -h ${BITCASTER_DATABASE_HOST} -p ${BITCASTER_DATABASE_PORT} -U postgres -c "CREATE DATABASE bitcaster"


reset-migrations: .init-db
	find src -name '000[1,2,3,4,5,6,7,8,9]*' | xargs rm -f
	./manage.py makemigrations bitcaster
	./manage.py makemigrations --check
	bitcaster upgrade --no-input
	bitcaster reindex

test:
	py.test tests -v --create-db

lint:
	pipenv run pre-commit run --all-files

messages:
	cd src && ../manage.py makemessages -l en -l fr -l es
	cd src && ../manage.py compilemessages -l en -l fr -l es

clean:
	rm -fr ${BUILDDIR} build dist src/*.egg-info .coverage coverage.xml .eggs .pytest_cache *.egg-info
	find src -name __pycache__ -o -name "*.py?" -o -name "*.orig" -prune | xargs rm -rf
	find tests -name __pycache__ -o -name "*.py?" -o -name "*.orig" -prune | xargs rm -rf
	find src/bitcaster/locale -name django.mo | xargs rm -f

fullclean:
	rm -fr .tox .cache .venv node_modules
	$(MAKE) clean


docs: .mkbuilddir
	@mkdir -p ${BUILDDIR}/docs
	@sphinx-build -aE docs/ ${BUILDDIR}/docs
ifdef BROWSE
	firefox ${BUILDDIR}/docs/index.html
endif

i18n:
	tx pull -a
	cd src && django-admin makemessages --settings=bitcaster.config.settings --pythonpath=../src
	cd src && django-admin compilemessages --settings=bitcaster.config.settings --pythonpath=../src
	tx push -s
