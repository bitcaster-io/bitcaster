VERSION=2.0.0
BUILDDIR='~build'
PYTHONPATH:=${PWD}/tests/:${PWD}
DBENGINE?=pg
DJANGO?='last'
SUBDIRS:=$(wildcard plugins/bitcaster-*)
DEVPI_CACHE_URL?=""
BITCASTER_DATABASE_HOST?=127.0.0.1
BITCASTER_DATABASE_PORT?=5432
PIPVER:=$(shell pip --version | cut -d " " -f 2 | cut -d "." -f 1)

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
	@echo "requirements            compile .pip requirement files from .in"
	@echo ""
	@echo "DOCKER"
	@echo "docker-reset-dev        reset/rebuild development docker container"



static:
	webpack --mode development
	bitcaster upgrade --no-migrate --no-input

develop: .setup-git
	$(MAKE) .init-db
	pipenv clean
	pipenv sync
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
	bitcaster option set INITIALIZED 0

reset-migrations: .init-db
	find src -name '000[1,2,3,4,5,6,7,8,9]*' | xargs rm -f
	./manage.py makemigrations bitcaster
	./manage.py makemigrations --check
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
	rm -fr ${BUILDDIR} build dist src/*.egg-info .coverage coverage.xml .eggs
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


requirements:
	pipenv lock -r > src/requirements/install.pip
	pipenv lock -r -d > src/requirements/testing.pip

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

uninstall-plugins:
	@for dir in $(SUBDIRS); do \
		pip uninstall $$dir || exit 1; \
 	done


.check_pip:
    #check for preventing Module pip no attribute main
    #https://stackoverflow.com/questions/49839610/attributeerror-module-pip-has-no-attribute-main
	-@if [ ${PIPVER} -ne 9 ]; then \
		echo "Upgrading/Downgrading pip to 9.0.3"; \
		python3 -m pip install --user --upgrade pip==9.0.3; \
	fi

docker-reset-dev: .check_pip
	rm -fr ${PWD}/~build/docker/
	-@docker stop bitcaster-dev
	-@docker rm bitcaster-dev
	-@docker rmi --force bitcaster:dev
	docker build --rm --squash -t bitcaster:dev -f Dockerfile.dev .
	docker run --name=bitcaster-dev -p 8000:8000 -it -v ${PWD}:/usr/src/bitcaster -v ${PWD}/~build/docker/etc/:/etc/bitcaster -v ${PWD}/~build/docker/var/bitcaster/:/var/bitcaster bitcaster:dev
	docker start bitcaster-dev
	docker exec -it bitcaster-dev bitcaster devserver -b 0.0.0.0:8000

docker-reset-beta:
	@rm -fr ${PWD}/~build/docker/
	@-docker stop bitcaster-beta
	@-docker rm bitcaster-beta
	@-docker rmi --force bitcaster:beta
	pip wheel . -w ./dist --cache-dir /dist
	@for dir in $(SUBDIRS); do \
		pushd $$dir; \
		python setup.py sdist -d ../../dist || exit 1; \
		popd; \
 	done
	docker build --rm --squash -t bitcaster:beta -f Dockerfile .
#	docker-compose start db redis

.PHONY: test-plugins clean-plugins install-plugins
