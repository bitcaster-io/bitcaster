import os
from pathlib import Path

DEFAULT_CONFIG = os.path.expanduser('~/.bitcaster/conf')

DEFAULTS = dict(
    # REDIS_CONSTANCE_URL=(str, 'redis://localhost:6379/3'),
    CELERY_BROKER_URL=(str, 'redis://localhost:6379/2'),
    CELERY_TASK_ALWAYS_EAGER=(bool, False),
    DATABASE_URL=(str, 'psql://postgres:@127.0.0.1:5432/bitcaster'),
    DEBUG=(bool, False),
    FAKE_OTP=(bool, False),
    FERNET_KEYS=(list, []),
    MEDIA_ROOT=(str, str(Path('~/.bitcaster/media').expanduser())),
    ON_PREMISE=(bool, True),
    PLUGINS_AUTOLOAD=(bool, False),
    REDIS_CACHE_URL=(str, 'redis://localhost:6379/0?key_prefix=bs'),
    REDIS_LOCK_URL=(str, 'redis://localhost:6379/1?key_prefix=bs-lock&backend=django_redis.cache.RedisCache'),
    SECRET_KEY=(str, ''),
    SENTRY_DSN=(str, ''),
    SENTRY_ENABLED=(bool, False),
    STATIC_ROOT=(str, str(Path(__file__).parent.parent / 'static')),
    URL_PREFIX=(str, ''),
)
