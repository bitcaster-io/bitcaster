RELEASE=.alpine
DOCKER_IMAGE=bitcaster/demo:1.1
BUILD_OPTIONS?=--squash
DOCKERFILE?=docker/Dockerfile.dev${RELEASE}
PYPI_SERVER?="pypi.org"
PYPI_INDEX?="https://${PYPI_SERVER}/simple/"
EXTRA?=-d

builder:
	cd .. && docker build ${BUILD_OPTIONS} \
			--target builder \
			--build-arg PYPI_SERVER=${PYPI_SERVER} \
			--build-arg PYPI_INDEX=${PYPI_INDEX} \
			-t ${DOCKER_IMAGE} \
			-f ${DOCKERFILE} .
clean:
	-docker stop bitcaster_demo
	-docker rmi ${DOCKER_IMAGE}

fullclean: clean
	-rm -fr ../~build/volumes

push:
	docker login -u saxix
	docker tag ${DOCKER_IMAGE} ${DOCKER_IMAGE}
	docker push ${DOCKER_IMAGE}

build:
	cd .. && docker build ${BUILD_OPTIONS} \
			--build-arg VCS_REF=`git rev-parse --short HEAD` \
			--build-arg BUILD_DATE=`date -u +"%Y-%m-%dT%H:%M:%SZ"` \
			--build-arg PYPI_SERVER=${PYPI_SERVER} \
			--build-arg PYPI_INDEX=${PYPI_INDEX} \
			-t ${DOCKER_IMAGE} \
			-f ${DOCKERFILE} .

run:
	cd .. && docker run -p 8000:8000 --rm \
			${EXTRA} \
			-e PGDATA=/var/postgresql/data \
			-e BITCASTER_CONF_DIR=/etc/bitcaster \
			-e BITCASTER_CONF=/etc/bitcaster/conf \
			-v $$PWD/~build/volumes/data:/var/postgresql/data \
			-v $$PWD/~build/volumes/etc/bitcaster:/etc/bitcaster \
			-v $$PWD/~build/volumes/var/bitcaster:/var/bitcaster \
			--name bitcaster_demo \
			${DOCKER_IMAGE} \
			${CMD}

test:
#	CMD="\"sh -c \'python -c \\\"import sir\'\\\"\"" $(MAKE) run
	CMD='bitcaster check --deploy' $(MAKE) run

shell:
#	CMD="\"sh -c \'python -c \\\"import sir\'\\\"\"" $(MAKE) run
	EXTRA='-it' CMD='/bin/sh' $(MAKE) run
