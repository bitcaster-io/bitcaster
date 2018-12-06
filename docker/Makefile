# envs to set before use this script
DATABASE_URL?=
DATABASE_URL_ETOOLS?=
DEVELOP?=0
DOCKER_PASS?=
DOCKER_USER?=
TARGET?=dev
# below vars are used internally
BUILD_OPTIONS?=--squash
CMD?=bitcaster
CONTAINER_NAME?=bitcaster-${TARGET}
ORGANIZATION=bitcaster
IMAGE_NAME=bitcaster
DOCKER_IMAGE_NAME=${ORGANIZATION}/${IMAGE_NAME}
DOCKER_IMAGE=${DOCKER_IMAGE_NAME}:${TARGET}
DOCKERFILE?=Dockerfile
RUN_OPTIONS?=
PIPENV_ARGS?=

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
			-t ${DOCKER_IMAGE} \
			-f docker/${DOCKERFILE} .
	docker tag ${DOCKER_IMAGE_NAME}:${TARGET} ${DOCKER_IMAGE_NAME}:dev
#	flatten image
#	docker create --name foo ${DOCKER_IMAGE_NAME}:${TARGET}
#	docker export foo | docker import - unicef/datamart:${TARGET}
#	docker rm foo
	docker images | grep ${DOCKER_IMAGE_NAME}


.run:
	cd .. && docker run \
	 		--rm \
	 		--name=${CONTAINER_NAME} \
			-p 8000:8000 \
			-e CACHE_URL=redis://127.0.0.1:6379/1 \
			-e CELERY_BROKER_URL=redis://127.0.0.1:6379/2 \
			-e CELERY_RESULT_BACKEND=redis://127.0.0.1:6379/3 \
			-e CSRF_COOKIE_SECURE=false \
			-e DATABASE_URL=${DATABASE_URL} \
			-e DATABASE_URL_ETOOLS=${DATABASE_URL_ETOOLS} \
			-e DEBUG=true \
			-e DJANGO_SETTINGS_MODULE=etools_datamart.config.settings \
			-e SECURE_BROWSER_XSS_FILTER=0 \
			-e SECURE_CONTENT_TYPE_NOSNIFF=0 \
			-e SECURE_FRAME_DENY=0 \
			-e SECURE_HSTS_SECONDS=0 \
			-e SECURE_HSTS_PRELOAD=false \
			-e SECURE_SSL_REDIRECT=false \
			-e SESSION_COOKIE_HTTPONLY=false \
			-e SESSION_COOKIE_SECURE=false \
			-e STATIC_ROOT=/var/datamart/static/ \
			-e DEVELOPMENT_MODE=0 \
			-e STACK=1 \
			-e X_FRAME_OPTIONS="SAMEORIGIN" \
			-v $$PWD/~build/volumes/var/datamart:/var/datamart/ \
			${RUN_OPTIONS} \
			${DOCKER_IMAGE} \
			${CMD}

local:
	RUN_OPTIONS="-v ${PWD}/..:/code -e PYTHONPATH=/code -it" \
	CMD="/bin/bash" \
	$(MAKE) .run

release:
	docker login -u ${DOCKER_USER} -p ${DOCKER_PASS}
	docker tag ${DOCKER_IMAGE_NAME}:${TARGET} ${DOCKER_IMAGE_NAME}:latest
	docker push ${DOCKER_IMAGE_NAME}:latest
	docker push ${DOCKER_IMAGE_NAME}:${TARGET}
	wget https://hooks.microbadger.com/images/bitcaster/demo/6gZxAyENUmnjeP10rFqqv3RVNeU=

run:
	$(MAKE) .run

test:
	RUN_OPTIONS="-e DEBUG=0 \
				 -e X_FRAME_OPTIONS=DENY \
				 -e SESSION_COOKIE_SECURE=1 \
				 -e CSRF_COOKIE_SECURE=1 \
				 -e SECURE_HSTS_PRELOAD=1 \
				 -e SECURE_SSL_REDIRECT=1" \
	CMD='bash -c "touch /var/datamart/.touch && django-admin check --deploy "' \
	$(MAKE) .run

scratch:
	RUN_OPTIONS=-it CMD='/bin/bash' $(MAKE) .run

shell:
#	docker exec -it ${CONTAINER_NAME} /bin/bash
	RUN_OPTIONS=-it CMD='/bin/bash' $(MAKE) .run

docker-remove:
	docker-remove.sh ${IMAGE_NAME} -o ${ORGANIZATION}
