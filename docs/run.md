# Run


    docker pull bitcaster/bitcaster:latest

To check possible configuration use

    docker run -t bitcaster/bitcaster:latest config


Below e general bash instruction. See [configuration](configuration.md) for details

    docker run \
		--rm \
		--name=bitcaster \
		-p 8000:8000 \
		-e ADMINS="${ADMINS}" \
		-e ADMIN_EMAIL="${ADMIN_EMAIL}" \
		-e ADMIN_PASSWORD="${ADMIN_PASSWORD}" \
		-e ALLOWED_HOSTS="*" \
		-e CACHE_URL="redis://redis:6379/1?client_class=django_redis.client.DefaultClient" \
		-e CELERY_BROKER_URL="redis://redis:6379/9" \
		-e CSRF_COOKIE_SECURE="true" \
		-e CSRF_TRUSTED_ORIGINS=... \
		-e DATABASE_URL="postgres://postgres:@db:5432/bitcaster" \
		-e EMAIL_FROM_EMAIL="${EMAIL_FROM_EMAIL}" \
		-e EMAIL_HOST_USER="${EMAIL_HOST_USER}" \
		-e EMAIL_HOST_PASSWORD="${EMAIL_HOST_PASSWORD}" \
		-e SECRET_KEY="ljhlijhlkjhlkjhlkhgkjhgkjhghgdtewrtdsxrews" \
		-e SECURE_SSL_REDIRECT=False \
		-e SESSION_COOKIE_DOMAIN= \
		-e SESSION_COOKIE_SECURE=True \
		-t bitcaster/bitcaster:latest

To see a full stack example please have a look to the provided [compose files]() file 
