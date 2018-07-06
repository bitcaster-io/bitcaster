RELEASE=.alpine
DOCKER_IMAGE=bitcaster/demo
BUILD_OPTIONS?=--squash
DOCKERFILE?=docker/Dockerfile.dev${RELEASE}
PYPI_SERVER?="pypi.org"
PYPI_INDEX?="https://${PYPI_SERVER}/simple/"


builder:
	cd .. && docker build ${BUILD_OPTIONS} \
			--target builder \
			--build-arg PYPI_SERVER=${PYPI_SERVER} \
			--build-arg PYPI_INDEX=${PYPI_INDEX} \
			-t ${DOCKER_IMAGE} \
			-f ${DOCKERFILE} .
clean:
	-docker rmi ${DOCKER_IMAGE}
#	-docker rmi `docker images -q -f "reference=${DOCKER_IMAGE}"`


build:
	cd .. && docker build ${BUILD_OPTIONS} \
			--build-arg PYPI_SERVER=${PYPI_SERVER} \
			--build-arg PYPI_INDEX=${PYPI_INDEX} \
			--build-arg GITHUB_CREDENTIALS=${GITHUB_CREDENTIALS} \
			-t ${DOCKER_IMAGE} \
			-f ${DOCKERFILE} .

run:
	cd .. && docker run -p 8000:8000 --rm \
			-e PGDATA=/var/postgresql/data \
			-e BITCASTER_CONF_DIR=/etc/bitcaster \
			-e BITCASTER_CONF=/etc/bitcaster/conf \
			-v $$PWD/~build/volumes/data:/var/postgresql/data \
			-v $$PWD/~build/volumes/etc/bitcaster:/etc/bitcaster \
			-it ${DOCKER_IMAGE} \
			${CMD}

test:
#	CMD="\"sh -c \'python -c \\\"import sir\'\\\"\"" $(MAKE) run
	CMD='django-admin check --deploy' $(MAKE) run

shell:
#	CMD="\"sh -c \'python -c \\\"import sir\'\\\"\"" $(MAKE) run
	CMD='/bin/sh' $(MAKE) run
