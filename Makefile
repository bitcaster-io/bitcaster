VERSION=2.0.0
BUILDDIR='~build'
PYTHONPATH:=${PWD}/tests/:${PWD}
DBENGINE?=pg
DJANGO?='last'
SUBDIRS:=$(wildcard plugins/bitcaster-*)
DEVPI_CACHE_URL?=""
BITCASTER_DATABASE_HOST?=127.0.0.1
BITCASTER_DATABASE_PORT?=5432

.mkbuilddir:
	mkdir -p ${BUILDDIR}

help:
	@echo "develop                 setup development environment"
	@echo "qa                      run quality assurance test"
	@echo "clean                   clean dev environment"
	@echo "fullclean               totally remove any development related files"
	@echo "static                  run webpack to compile static files"
	@echo "messages                create translations files"
	@echo ""
	@echo "DANGEROUS COMMANDS"
	@echo "reset-migrations        reset all database migrations"
	@echo "reset-dev-env           reset dev environment"
	@echo "compile-requirements    compile .pip requirement files from .in"
	@echo "sync-requirements       sync virtualenv to only contains bitcaster requirements"



static:
	webpack --mode development
	bitcaster upgrade --no-migrate --no-input

develop: .setup-git
	@pip install -U pip-tools
	$(MAKE) .init-db sync-requirements
	npm install

.setup-git:
	git config branch.autosetuprebase always
	chmod +x hooks/*
	cd .git/hooks && ln -fs ../../hooks/* .

.init-db:
	# initializing '${DBENGINE}' database 'bitcaster'
	dropdb --if-exists -h ${BITCASTER_DATABASE_HOST} -p ${BITCASTER_DATABASE_PORT} -U postgres test_bitcaster
	dropdb --if-exists -h ${BITCASTER_DATABASE_HOST} -p ${BITCASTER_DATABASE_PORT} -U postgres bitcaster
	createdb -h ${BITCASTER_DATABASE_HOST} -p ${BITCASTER_DATABASE_PORT} -U postgres bitcaster

reset-dev-env: .init-db
	bitcaster upgrade --no-input

reset-migrations: .init-db
	find src -name '000[1,2,3,4,5,6,7,8,9]*' | xargs rm -f
	./manage.py makemigrations bitcaster
	bitcaster upgrade --no-input
	bitcaster option set INITIALIZED 0

test:
	py.test tests -v --create-db

qa:
	flake8 src/ tests/
	isort -rc src/ --check-only
	check-manifest

messages:
	cd src && ../manage.py makemessages -l en -l fr -l es
	cd src && ../manage.py compilemessages -l en -l fr -l es

clean:
	rm -fr ${BUILDDIR} dist *.egg-info .coverage coverage.xml .eggs
	find src -name __pycache__ -o -name "*.py?" -o -name "*.orig" -prune | xargs rm -rf
	find tests -name __pycache__ -o -name "*.py?" -o -name "*.orig" -prune | xargs rm -rf
	find src/concurrency/locale -name django.mo | xargs rm -f

fullclean:
	rm -fr .tox .cache
	$(MAKE) clean
	$(MAKE) clean-plugins


docs: .mkbuilddir
	mkdir -p ${BUILDDIR}/docs
	sphinx-build -aE docs/ ${BUILDDIR}/docs
ifdef BROWSE
	firefox ${BUILDDIR}/docs/index.html
endif

compile-requirements:
	pip install pip-tools devpi-builder
	@pip-compile src/requirements/install.in \
		--upgrade \
		--annotate \
		--rebuild \
		--no-header \
		--no-emit-trusted-host \
		--no-index -o src/requirements/install.pip
	@pip-compile src/requirements/testing.in \
		src/requirements/install.pip \
		--upgrade \
		--annotate \
		--rebuild \
		--no-header \
		--no-emit-trusted-host \
		--no-index -o src/requirements/testing.pip
	@pip-compile src/requirements/develop.in \
		src/requirements/testing.pip \
		--upgrade \
		--annotate \
		--rebuild \
		--no-header \
		--no-emit-trusted-host \
		--no-index -o src/requirements/develop.pip

sync-requirements:
	pip-sync src/requirements/develop.pip
	pip install -e .[dev]
	$(MAKE) install-plugins

cache-requirements:
	devpi-builder src/requirements/develop.pip  ${DEVPI_CACHE_URL}

test-all:
	pytest tests
	$(MAKE) test-plugins

test-plugins:
	@for dir in $(SUBDIRS); do \
		pytest $$dir/tests || exit 1; \
 	done

clean-plugins:
	@for dir in $(SUBDIRS); do \
		pushd $$dir;\
		make clean; \
		popd; \
 	done

tox-plugins:
	@for dir in $(SUBDIRS); do \
		pushd $$dir;\
		tox || exit 1; \
		popd; \
 	done

install-plugins:
	@for dir in $(SUBDIRS); do \
		pip install -e $$dir || exit 1; \
 	done

docker-beta:
	docker rm bitcaster-beta
	docker build --rm -t bitcaster:beta -f Dockerfile .
	docker run --name=bitcaster-beta -p 8000:8000 -it -v ${PWD}:/usr/src/bitcaster -v ${PWD}/~build/etc/:/etc/bitcaster -v ${PWD}/~build/var/bitcaster/:/var/bitcaster bitcaster:beta
	docker start bitcaster-beta

.PHONY: test-plugins clean-plugins install-plugins
