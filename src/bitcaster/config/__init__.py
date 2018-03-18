import os
from pathlib import Path

DEFAULT_CONFIG = os.path.expanduser('~/.bitcaster/conf')

DEFAULTS = dict(
    CELERY_BROKER_URL=(str, 'redis://localhost:6379/2'),
    CELERY_TASK_ALWAYS_EAGER=(bool, False),
    DATABASE_URL=(str, 'psql://postgres:@127.0.0.1:5432/bitcaster'),
    DEBUG=(bool, False),
    ENABLE_SENTRY=(bool, False),
    FAKE_OTP=(bool, False),
    MEDIA_ROOT=(str, str(Path('~/.bitcaster/media').expanduser())),
    ON_PREMISE=(bool, True),
    ORGANIZATION=(str, 'Bitcaster'),
    PLUGINS_AUTOLOAD=(bool, False),
    REDIS_CACHE_URL=(str, 'redis://localhost:6379/0'),
    # REDIS_CONSTANCE_URL=(str, 'redis://localhost:6379/3'),
    REDIS_LOCK_URL=(str, 'redis://localhost:6379/1'),
    SECRET_KEY=(str, ''),
    SENTRY_DSN=(str, ''),
    STATIC_ROOT=(str, str(Path('~/.bitcaster/static').expanduser())),
)
