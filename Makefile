VERSION=2.0.0
BUILDDIR='~build'
PYTHONPATH:=${PWD}/tests/:${PWD}
DBENGINE?=pg
DJANGO?='last'
SUBDIRS := $(wildcard plugins/mercury-*)


.mkbuilddir:
	mkdir -p ${BUILDDIR}

help:
	echo "develop"
	echo "reset-migrations"

develop: .setup-git
	@pip install -U pip-tools
	$(MAKE) .init-db sync-requirements
	npm install

.setup-git:
	git config branch.autosetuprebase always
	chmod +x hooks/*
	cd .git/hooks && ln -fs ../../hooks/* .

.init-db:
	# initializing '${DBENGINE}' database 'mercury'
	dropdb --if-exists -h 127.0.0.1 -U postgres test_mercury
	dropdb --if-exists -h 127.0.0.1 -U postgres mercury
	createdb -h 127.0.0.1 -U postgres mercury

.reset-env: .init-db
	bitcaster option set INITIALIZED 0
	bitcaster upgrade --no-input

reset-migrations: .init-db
	find src -name '000[1,2,3,4,5,6,7,8,9]*' | xargs rm -f
	./manage.py makemigrations mercury
	./manage.py migrate
	./manage.py constance set INITIALIZED 0

#	find extras -name '000[1,3,4,5,6,7,8,9]*' | xargs rm -f
#	./manage.py makemigrations geo

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
	devpi-builder src/requirements/develop.pip  http://localhost:3141/sax/cache --user sax

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


.PHONY: test-plugins clean-plugins install-plugins
