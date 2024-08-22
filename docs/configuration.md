# Environment Variables

## General 


### ADMIN_EMAIL
Default: ``

Username/Email of the initial user. Created at first deploy

### ADMIN_PASSWORD
Default: ``

Password for initial user created at first deploy. It is ignored if `ADMIN_EMAIL` exists

### ALLOWED_HOSTS
Default: "127.0.0.1,localhost"  

A list of strings representing the host/domain names that this Django site can serve. This is a security measure to prevent HTTP Host header attacks, which are possible even under many seemingly-safe web server configurations.

see <https://docs.djangoproject.com/en/5.0/ref/settings#allowed-hosts>


### CACHE_URL
Default: ``

Redis URL to use as cache backend.

Es: `redis://192.168.66.66:6379/1?client_class=django_redis.client.DefaultClient`


see <https://docs.djangoproject.com/en/5.1/topics/cache/>

### CELERY_BROKER_URL
Default: ``

see <https://docs.celeryq.dev/en/stable/django/first-steps-with-django.html>


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



### MEDIA_ROOT  
Default: `/var/run/app/media`

Read more at <https://docs.djangoproject.com/en/5.1/ref/settings/#media-root


### SECRET_KEY
Default: `<- not set ->`  

see <https://docs.djangoproject.com/en/5.0/ref/settings#secret-key>

### SECURE_HSTS_PRELOAD
Default: `True`  

see <https://docs.djangoproject.com/en/5.0/ref/settings#secure-hsts-preload

### SECURE_HSTS_SECONDS
Default: `60`  

see <https://docs.djangoproject.com/en/5.0/ref/settings#secure-hsts-seconds
### SECURE_SSL_REDIRECT
Default: `True`  

see <https://docs.djangoproject.com/en/5.0/ref/settings#secure-ssl-redirect

### SENTRY_DSN
Default: ``

Sentry DSN

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


### STORAGE_MEDIA= 
Default: ''

Storage to use for media files. STORAGE_DEFAULT is used if not set

see <https://docs.djangoproject.com/en/5.0/ref/settings#storages>


### STORAGE_STATIC
Default: `django.core.files.storage.FileSystemStorage`

see <https://docs.djangoproject.com/en/5.0/ref/settings#storages>


### TIME_ZONE
Default: `UTC`  
see <https://docs.djangoproject.com/en/5.0/ref/settings#std-setting-TIME_ZONE>

## Advanced Configuration

!!! Warning
    
    Do not change these settings in production environment


### CATCH_ALL_EMAIL
Default: ``

If set all the emails will be sent to this address 

### CELERY_TASK_ALWAYS_EAGER
Default: false

see <https://docs.celeryq.dev/en/stable/userguide/configuration.html#std-setting-task_always_eager>

### CELERY_TASK_EAGER_PROPAGATES
Default: True  

see <https://docs.celeryq.dev/en/stable/userguide/configuration.html#task-eager-propagates>


### CELERY_VISIBILITY_TIMEOUT
Default: 1800  

see <https://docs.celeryq.dev/en/stable/userguide/configuration.html#broker-transport-options>

###CSRF_COOKIE_SAMESITE

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
Default: `/var/run/app/static`  
see <https://docs.djangoproject.com/en/5.0/ref/settings#static-root>
