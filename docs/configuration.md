# Settings

!!! NOTE ""

    **Bitcaster uses "security-first" approach**

    All the settings have the safest default value (es. `DEBUG=False` or `SESSION_COOKIE_SECURE=True`);
    this could create some issues in some environments (es. staging or development).
    Keep this in consideration when you configure your installation.

    run `docker run -t bitcaster/bitcaster:latest config` or `django-admin env` to check your configuration


## General

### ADMIN_EMAIL
Default: ``

Username and Email of the initial user. Created at first deploy

!!! warning

    This variable has effect only the first time Bitcaster starts. Any attempt to change it later will produce a startup error



### ADMIN_PASSWORD
Default: ``

Password for initial user created at first deploy. It is ignored if `ADMIN_EMAIL` exists

!!! warning

    This variable has effect only the first time Bitcaster starts. Any attempt to change it later will produce a startup error


### BITCASTER_DOCUMENTATION_SITE_URL
Default: `https://docs.bitcaster.io`

Base URL of the Bitcaster documentation site (no trailing slash). It is used
by the admin "help" links to point to the online documentation.


### AGENT_FILESYSTEM_ROOT
Default: ``

Base path allowed by the local filesystem <glossary:Agent>



### AGENT_FILESYSTEM_VALIDATOR
Default: `bitcaster.agents.fs.validate_path`

Callable that validates the path used by the local filesystem <glossary:Agent>.


### AGENT_FILESYSTEM_DISALLOWED
Default: ``

List of directories disallowed for the local filesystem <glossary:Agent>.


### ALLOWED_HOSTS
Default: "127.0.0.1,localhost"

A list of strings representing the host/domain names that this Django site can serve. This is a security measure to prevent HTTP Host header attacks, which are possible even under many seemingly-safe web server configurations.

see <https://docs.djangoproject.com/en/5.0/ref/settings#allowed-hosts>


### AUTHENTICATION_BACKENDS
Default: ``

Django authentication backends used by the site.

see <https://docs.djangoproject.com/en/5.0/ref/settings#authentication-backends>


### CACHE_PREFIX
Default: ``

Prefix string to use in cache keys.


### CACHE_URL
Default: `redis://cache-server:6379/0`

Redis URL to use as cache backend.

Es: `redis://192.168.66.66:6379/1?client_class=django_redis.client.DefaultClient`

!!! note

    Do not change client_class if you are not sure, use `django_redis.client.DefaultClient`

see <https://docs.djangoproject.com/en/5.1/topics/cache/>

### DRAMATIQ_BROKER
Default: `redis://dramatiq-broker:6379/0`

Redis URL used as broker for background tasks.

see <https://dramatiq.io/reference.html#brokers>


### ENVIRONMENT
Default: `production`

Bitcaster environment name. It is displayed in the admin header and tunes
runtime behaviour (e.g. `local` enables development helpers).


### CHANNEL_SERVER
Default: `channel-server:6379`

Redis URL used by the async channel layer for realtime notifications.


### CSRF_TRUSTED_ORIGINS
Default: "http://localhost,http://127.0.0.1"

see <https://docs.djangoproject.com/en/5.1/ref/settings/#csrf-trusted-origins>


### DATABASE_URL
Default: sqlite:///bitcaster.db

see <https://django-environ.readthedocs.io/en/latest/types.html#environ-env-db-url>


### MEDIA_FILE_STORAGE
Default: django.core.files.storage.FileSystemStorage

see <https://docs.djangoproject.com/en/5.0/ref/settings#storages>


### MEDIA_URL
Default: `/media/`

see <https://docs.djangoproject.com/en/5.0/ref/settings#media-url>


### REDIRECT_TO_HTTPS
Default: `false`

Redirect all HTTP traffic to HTTPS.


### CLIENT_TOKEN_TTL
Default: `900`

Lifetime in seconds of client tokens minted via the token exchange endpoint.
Client tokens are short-lived credentials meant to be used from web pages.


### CORS_ALLOWED_ORIGINS
Default: ``

Explicit allowlist of origins allowed to call the public API from a browser.
Use full origins without trailing slash, e.g. `https://example.com`.

Requests carrying an `Origin` header are only served CORS headers when the
origin is listed here. Combined with web API keys and client tokens, this
prevents other websites from using credentials embedded in your pages.


### TRIGGER_CONTEXT_MAX_SIZE
Default: `32768`

Maximum size in bytes of the serialized `context` payload accepted from web
credentials (web API keys and client tokens) on the trigger endpoint.


### SECRET_KEY
Default: ``

see <https://docs.djangoproject.com/en/5.0/ref/settings#secret-key>

### SECURE_HSTS_PRELOAD
Default: `True`

see <https://docs.djangoproject.com/en/5.0/ref/settings#secure-hsts-preload>

### SECURE_HSTS_SECONDS
Default: `60`

see <https://docs.djangoproject.com/en/5.0/ref/settings#secure-hsts-seconds>


### SECURE_PROXY_SSL_HEADER
Default: ``

Header used to detect an HTTPS request behind a reverse proxy.

see <https://docs.djangoproject.com/en/5.0/ref/settings#secure-proxy-ssl-header>

### SECURE_SSL_REDIRECT
Default: `True`

see <https://docs.djangoproject.com/en/5.0/ref/settings#secure-ssl-redirect>

### SENTRY_DSN
Default: ``

[Sentry](https://sentry.io) DSN

### SENTRY_ENVIRONMENT
Default: `production`

Sentry Environment

### SENTRY_URL
Default: ``

Sentry server url

### SESSION_COOKIE_DOMAIN
Default: `bitcaster.io`

see <https://docs.djangoproject.com/en/5.0/ref/settings#std-setting-SESSION_COOKIE_DOMAIN>

### SESSION_COOKIE_HTTPONLY
Default: `True`
see <https://docs.djangoproject.com/en/5.0/ref/settings#session-cookie-httponly>

### SESSION_COOKIE_NAME
Default: `bitcaster_session`
see <https://docs.djangoproject.com/en/5.0/ref/settings#session-cookie-name>

### SESSION_COOKIE_PATH
Default: `/`
see <https://docs.djangoproject.com/en/5.0/ref/settings#session-cookie-path>

### SESSION_COOKIE_SECURE
Default: `True`
see <https://docs.djangoproject.com/en/5.0/ref/settings#session-cookie-secure>

### SOCIAL_AUTH_REDIRECT_IS_HTTPS
Default: `True`
see <https://python-social-auth.readthedocs.io/en/latest/configuration/settings.html>

### STATIC_FILE_STORAGE
Default: `django.core.files.storage.FileSystemStorage`
see <https://docs.djangoproject.com/en/5.0/ref/settings#storages>

### STATIC_URL
Default: `/static/`

see <https://docs.djangoproject.com/en/5.0/ref/settings#static-url>

see <https://docs.djangoproject.com/en/5.0/ref/settings#storages>


### STORAGE_DEFAULT
Default: `django.core.files.storage.FileSystemStorage`

Default Storage

see <https://docs.djangoproject.com/en/5.0/ref/settings#storages>


### STORAGE_MEDIA
Default: ''

Storage to use for media files. STORAGE_DEFAULT is used if not set

see <https://docs.djangoproject.com/en/5.0/ref/settings#storages>


### STORAGE_STATIC
Default: `django.core.files.storage.FileSystemStorage`

see <https://docs.djangoproject.com/en/5.0/ref/settings#storages>


### SUPERUSERS
Default: ``

Comma-separated list of users that are granted superuser privileges when
created.


### TIME_ZONE
Default: `UTC`
see <https://docs.djangoproject.com/en/5.0/ref/settings#std-setting-TIME_ZONE>

## Advanced Configuration

!!! Warning

    Do not change these settings in production environment


### CATCH_ALL_EMAIL
Default: ``

If set all the emails will be sent to this address

### CSRF_COOKIE_SAMESITE

see <https://docs.djangoproject.com/en/5.0/ref/settings#csrf-cookie-samesite>

### CSRF_COOKIE_SECURE
Default: True

see <https://docs.djangoproject.com/en/5.0/ref/settings#csrf-cookie-secure>



### DEBUG
Default: `false`

see <https://docs.djangoproject.com/en/5.0/ref/settings#debug>


### DJANGO_SETTINGS_MODULE
Default: `bitcaster.config.settings`


Read more at <https://docs.djangoproject.com/en/5.1/topics/settings/#designating-the-settings>

### EMAIL_BACKEND
Default: django.core.mail.backends.smtp.EmailBackend

see <https://docs.djangoproject.com/en/5.0/ref/settings#email-backend>

### EMAIL_HOST
Default: ``

see <https://docs.djangoproject.com/en/5.0/ref/settings#email-host>

### EMAIL_HOST_PASSWORD
Default: ``

see <https://docs.djangoproject.com/en/5.0/ref/settings#email-host-password>

### EMAIL_HOST_USER
Default: ``

see <https://docs.djangoproject.com/en/5.0/ref/settings#email-host-user>

### EMAIL_PORT
Default: 25

see <https://docs.djangoproject.com/en/5.0/ref/settings#email-port>
### EMAIL_SUBJECT_PREFIX
Default: `[Bitcaster]`

see <https://docs.djangoproject.com/en/5.0/ref/settings#email-subject-prefix>

### EMAIL_TIMEOUT
Default: ``

see <https://docs.djangoproject.com/en/5.0/ref/settings#email-timeout>

### EMAIL_USE_LOCALTIME
Default: ``

see <https://docs.djangoproject.com/en/5.0/ref/settings#email-use-localtime>


### EMAIL_USE_SSL
Default: False
see <https://docs.djangoproject.com/en/5.0/ref/settings#email-use-ssl>

### EMAIL_USE_TLS
Default: False

see <https://docs.djangoproject.com/en/5.0/ref/settings#email-use-tls>

### EXTRA_APPS
Default: ``

Extra Django applications to load in addition to the default ones.

see <https://docs.djangoproject.com/en/5.0/ref/settings#installed-apps>


### INTERNAL_IPS
Default: ``

List of IP addresses that are trusted for debug tooling (e.g. the debug toolbar).

see <https://docs.djangoproject.com/en/5.0/ref/settings#internal-ips>


### LOGGING_LEVEL
Default: CRITICAL

see <https://docs.djangoproject.com/en/5.0/ref/settings#logging-level>

### MEDIA_ROOT
Default: `/var/run/app/media`

see <https://docs.djangoproject.com/en/5.0/ref/settings#media-root>

### SIGNING_BACKEND
Default: `django.core.signing.TimestampSigner`
see <https://docs.djangoproject.com/en/5.0/ref/settings#signing-backend>


### SOCIAL_AUTH_LOGIN_URL
Default: `/login/`
see <https://python-social-auth.readthedocs.io/en/latest/configuration/settings.html#urls-options>

### SOCIAL_AUTH_RAISE_EXCEPTIONS
Default: False
see <https://python-social-auth.readthedocs.io/en/latest/configuration/django.html>


### STATIC_ROOT
Default: `/var/bitcaster/static`
see <https://docs.djangoproject.com/en/5.0/ref/settings#static-root>

### USE_X_FORWARDED_HOST
Default: `False`

Use the `X-Forwarded-Host` header from the proxy as the host name.

see <https://docs.djangoproject.com/en/5.0/ref/settings#use-x-forwarded-host>

### USE_X_FORWARDED_PORT
Default: `False`

Use the `X-Forwarded-Port` header from the proxy as the port.

see <https://docs.djangoproject.com/en/5.0/ref/settings#use-x-forwarded-port>
