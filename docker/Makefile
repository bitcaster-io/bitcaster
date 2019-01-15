# envs to set before use this script
BITCASTER_DATABASE_URL?=${BITCASTER_DATABASE_URL}
BITCASTER_SECRET_KEY?=${BITCASTER_SECRET_KEY}
DEVELOP?=0
DOCKER_PASS?=
DOCKER_USER?=
TARGET?=0.3.0a12
BUILD_DATE:="$(shell date +"%Y-%m-%d %H:%M")"
# below vars are used internally
BUILD_OPTIONS?=--squash
CMD?=stack
CONTAINER_NAME?=bitcaster-${TARGET}
ORGANIZATION=bitcaster
IMAGE_NAME=bitcaster
DOCKER_IMAGE_NAME=${ORGANIZATION}/${IMAGE_NAME}
DOCKER_IMAGE=${DOCKER_IMAGE_NAME}:${TARGET}
DOCKERFILE?=Dockerfile
RUN_OPTIONS?=
PIPENV_ARGS?=
VOLUME=~build/volumes/var/bitcaster/

help:
	@echo "dev                  build dev image (based on local code)"
	@echo "build                build production image (based on tag ${TARGET})"
	@echo "release              release tag ${TARGET} on docker hub"
	@echo "run                  run ${DOCKER_IMAGE} locally"

build-base:
	docker build --target base \
			-t ${DOCKER_IMAGE_NAME}:base \
			-f docker/${DOCKERFILE} .

build:
	cd .. && docker build \
			${BUILD_OPTIONS} \
			--build-arg DEVELOP=${DEVELOP} \
			--build-arg GITHUB_CREDENTIALS=${GITHUB_CREDENTIALS} \
			--build-arg VERSION=${TARGET} \
			--build-arg BUILD_DATE=${BUILD_DATE} \
			-t ${DOCKER_IMAGE} \
			-f docker/${DOCKERFILE} .
	docker tag ${DOCKER_IMAGE_NAME}:${TARGET} ${DOCKER_IMAGE_NAME}:dev
#	flatten image
#	docker create --name foo ${DOCKER_IMAGE_NAME}:${TARGET}
#	docker export foo | docker import - unicef/datamart:${TARGET}
#	docker rm foo
	docker images | grep ${DOCKER_IMAGE_NAME}


.run:
	mkdir -p ../${VOLUME}
	cd .. && docker run \
	 		--rm \
	 		--name=${CONTAINER_NAME} \
			-p 8000:8000 \
			-p 15000:15000 \
			-e BITCASTER_SECRET_KEY="${BITCASTER_SECRET_KEY}" \
			-e BITCASTER_REDIS_CACHE_URL=${BITCASTER_REDIS_CACHE_URL} \
			-e BITCASTER_REDIS_LOCK_URL=${BITCASTER_REDIS_LOCK_URL} \
			-e BITCASTER_CELERY_BROKER_URL=${BITCASTER_CELERY_BROKER_URL} \
			-e BITCASTER_DATABASE_URL=${BITCASTER_DATABASE_URL} \
			-e BITCASTER_DEBUG=true \
			-v $$PWD/${VOLUME}:/var/bitcaster/ \
			${RUN_OPTIONS} \
			${DOCKER_IMAGE} \
			${CMD}

local:
	RUN_OPTIONS="-v ${PWD}/..:/code -e PYTHONPATH=/code -it" \
	CMD="/bin/bash" \
	$(MAKE) .run

release:
	pass docker/saxix | docker login -u saxix --password-stdin
	docker tag ${DOCKER_IMAGE_NAME}:${TARGET} ${DOCKER_IMAGE_NAME}:latest
	docker push ${DOCKER_IMAGE_NAME}:latest
	docker push ${DOCKER_IMAGE_NAME}:${TARGET}
	curl -XPOST https://hooks.microbadger.com/images/bitcaster/bitcaster/MQKzhkSXITqlkZMgcN1sQbKCnQo=
	cd .. && bumpversion --config-file=.bumpversion.cfg num
	lazo upgrade ${DOCKER_IMAGE_NAME}:${TARGET} --insecure

run:
	$(MAKE) .run

test:
	RUN_OPTIONS="-e BITCASTER_DEBUG=1 \
				 -e X_FRAME_OPTIONS=DENY \
				 -e SESSION_COOKIE_SECURE=1 \
				 -e CSRF_COOKIE_SECURE=1 \
				 -e SECURE_HSTS_PRELOAD=1 \
				 -e SECURE_SSL_REDIRECT=1" \
	CMD='bash -c "whoami && touch /var/bitcaster/.touch && bitcaster check --deploy && bitcaster plugin list"' \
	$(MAKE) .run

scratch:
	RUN_OPTIONS=-it CMD='/bin/bash' $(MAKE) .run

shell:
#	docker exec -it ${CONTAINER_NAME} /bin/bash
	RUN_OPTIONS=-it CMD='/bin/bash' $(MAKE) .run

docker-remove:
	docker-remove.sh ${IMAGE_NAME} -o ${ORGANIZATION}

ignore:
	cd .. && docker build -f docker/Dockerfile.ignore -t build-context .
	docker run --rm -it build-context

onbuild:
	DOCKER_IMAGE=Dockerfile.onbuild DOCKER_IMAGE=bitcaster:onbuild $(MAKE) build
