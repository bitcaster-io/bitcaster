VERSION=2.0.0
BUILDDIR='~build'
PYTHONPATH:=${PWD}/tests/:${PWD}
DBENGINE?=pg
DJANGO?='last'


.mkbuilddir:
	mkdir -p ${BUILDDIR}

develop:
	@pip install -U pip setuptools
	@sh -c "if [ '${DBENGINE}' = 'pg' ]; then pip install -q psycopg2; fi"
	@pip install -e .[dev]
	$(MAKE) .init-db


.init-db:
	# initializing '${DBENGINE}' database 'mercury'
	dropdb --if-exists -h 127.0.0.1 -U postgres test_mercury
	dropdb --if-exists -h 127.0.0.1 -U postgres mercury
	createdb -h 127.0.0.1 -U postgres mercury

reset-migrations: .init-db
	find src -name '000[1,2,3,4,5,6,7,8,9]*' | xargs rm -f
	./manage.py makemigrations mercury

test:
	py.test -v --create-db

qa:
	flake8 src/ tests/
	isort -rc src/ --check-only
	check-manifest


clean:
	rm -fr ${BUILDDIR} dist *.egg-info .coverage coverage.xml .eggs
	find src -name __pycache__ -o -name "*.py?" -o -name "*.orig" -prune | xargs rm -rf
	find tests -name __pycache__ -o -name "*.py?" -o -name "*.orig" -prune | xargs rm -rf
	find src/concurrency/locale -name django.mo | xargs rm -f

fullclean:
	rm -fr .tox .cache
	$(MAKE) clean


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
	pip install -e plugins/mercury-slack
	pip install -e plugins/mercury-xmpp
	pip install -e plugins/mercury-twilio
	pip install -e plugins/mercury-plivo
	pip install -e plugins/mercury-hangout
	pip install -e plugins/mercury-skype



cache-requirements:
	pip freeze > freeze.txt
	devpi-builder freeze.txt  http://localhost:3141/sax/dev --user sax
#	rm freeze.txt
