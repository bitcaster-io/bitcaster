# envs to set before use this script
#BITCASTER_DATABASE_URL?=${BITCASTER_DATABASE_URL}
#BITCASTER_SECRET_KEY?=${BITCASTER_SECRET_KEY}
DEVELOP?=0
DOCKER_PASS?=
DOCKER_USER?=
TARGET?=0.104.0a
BUILD_DATE:="$(shell date +"%Y-%m-%d %H:%M")"
# below vars are used internally
BUILD_OPTIONS?=--squash
CMD?=bitcaster
CONTAINER_NAME?=bitcaster-${TARGET}
#ORGANIZATION=bitcaster
#IMAGE_NAME=bitcaster
DOCKER_IMAGE_NAME=bitcaster/bitcaster
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
	@echo "ignore               run ${DOCKER_IMAGE} locally"
	@echo "bump	 				bump version"

build-base:
	cd .. && docker build \
			${BUILD_OPTIONS} \
			-t ${DOCKER_IMAGE_NAME}-0.4:base \
			-f docker/Dockerfile.base .
	cd .. && docker build \
			${BUILD_OPTIONS} \
			--build-arg TEST=--dev \
			-t ${DOCKER_IMAGE_NAME}-0.4:base-dev \
			-f docker/Dockerfile.base .

	pass docker/saxix | docker login -u saxix --password-stdin
	docker push ${DOCKER_IMAGE_NAME}-0.4:base
	docker push ${DOCKER_IMAGE_NAME}-0.4:base-dev
	docker images | grep ${DOCKER_IMAGE_NAME}


build:
	cd .. && docker build \
			${BUILD_OPTIONS} \
			--build-arg DEVELOP=${DEVELOP} \
			--build-arg VERSION=${TARGET} \
			--build-arg BUILD_DATE=${BUILD_DATE} \
			-t ${DOCKER_IMAGE} \
			-f docker/${DOCKERFILE} .
	docker images | grep ${DOCKER_IMAGE_NAME}


.run:
	mkdir -p ../${VOLUME}
	cd .. && docker run \
	 		--rm \
	 		--name=${CONTAINER_NAME} \
			-p 8000:8000 \
			-e BITCASTER_SECRET_KEY="${BITCASTER_SECRET_KEY}" \
			-e BITCASTER_FERNET_KEYS="${BITCASTER_FERNET_KEYS}" \
			-e BITCASTER_SENTRY_DSN="${BITCASTER_SENTRY_DSN}" \
			-e BITCASTER_SENTRY_ENABLED=True \
			-e BITCASTER_REDIS_CACHE_URL=${BITCASTER_REDIS_CACHE_URL} \
			-e BITCASTER_REDIS_TSDB_URL=${BITCASTER_REDIS_TSDB_URL} \
			-e BITCASTER_REDIS_LOCK_URL=${BITCASTER_REDIS_LOCK_URL} \
			-e BITCASTER_CELERY_BROKER_URL=${BITCASTER_CELERY_BROKER_URL} \
			-e BITCASTER_STATIC_ROOT=/var/bitcaster/static \
			-e BITCASTER_DATABASE_URL=${BITCASTER_DATABASE_URL} \
			-e BITCASTER_ADVANCED_MODE=1 \
			-e BITCASTER_ENABLE_IMPERSONATE=1 \
			-e BITCASTER_DEBUG=true \
			${RUN_OPTIONS} \
			${DOCKER_IMAGE} \
			${CMD}

#			-v $$PWD/${VOLUME}:/var/bitcaster/ \

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
	curl https://demo.bitcaster.io/api/o/os4d/a/5/e/${BITCASTER_DEPLOY_KEY}:18/tr/?version=${TARGET}

deploy:
#	lazo rancher shell bitcaster:bitcaster -- bitcaster backup --filename /backups3/latest.json
#	lazo rancher shell bitcaster:bitcaster -- circusctl stop
#	lazo rancher shell bitcaster:db -- dropdb -U postgres bitcaster;
#	lazo rancher shell bitcaster:db -- createdb -U postgres bitcaster;
	lazo rancher upgrade bitcaster:bitcaster bitcaster/bitcaster:${TARGET}
#	lazo rancher shell bitcaster:bitcaster -- bitcaster restore --filename /backups3/latest.json
	curl https://demo.bitcaster.io/api/o/os4d/a/5/e/${BITCASTER_DEPLOY_KEY}:13/tr/?version=${TARGET}

run:
	$(MAKE) .run

test:
	RUN_OPTIONS="-e BITCASTER_DEBUG=1 \
				 -e X_FRAME_OPTIONS=DENY \
				 -e SESSION_COOKIE_SECURE=1 \
				 -e CSRF_COOKIE_SECURE=1 \
				 -e SECURE_HSTS_PRELOAD=1 \
				 -e SECURE_SSL_REDIRECT=1" \
	CMD='sh -c "whoami && touch /var/bitcaster/.touch && bitcaster check --deploy && bitcaster upgrade"' \
	$(MAKE) .run


shell:
	DOCKER_IMAGE=${DOCKER_IMAGE_NAME}:latest RUN_OPTIONS=-it CMD='/bin/sh' $(MAKE) .run

stack:
	DOCKER_IMAGE=${DOCKER_IMAGE_NAME}:latest RUN_OPTIONS=-it CMD='stack' $(MAKE) .run

ignore:
	cd .. && docker build -f docker/Dockerfile.ignore -t build-context .
	docker run --rm -it build-context

backup:
	lazo rancher shell bitcaster:bitcaster -- bitcaster backup --filename /backups/backup.json
