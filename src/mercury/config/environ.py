# -*- coding: utf-8 -*-
# Load operating system environment variables and then prepare to use them
from environ import environ, warnings, re, os, ImproperlyConfigured
from mercury import logging
from pathlib import Path
import re
from mercury.config import DEFAULT_CONFIG

logger = logging.getLogger(__name__)

DEFAULTS=dict(
    DEBUG=False,

    MEDIA_ROOT='',
    STATIC_ROOT='',

    ENABLE_SENTRY=True,
    SENTRY_DSN='',
    MERCURY_PLUGINS_AUTOLOAD=False,

    EMAIL_USE_TLS=True,
    EMAIL_HOST='',
    EMAIL_HOST_USER='',
    EMAIL_HOST_PASSWORD='',
    EMAIL_PORT='',

    DATABASE_URL='',

    CELERY_BROKER_URL='',

    REDIS_CONNECTION='',
)

class Env(environ.Env):
    def get_value(self, var, cast=None, default=environ.Env.NOTSET, parse_default=False):
        try:

            value = super().get_value(var, cast, default, parse_default)
            # Resolve any proxied values
            if hasattr(value, 'startswith') and '${' in value:
                m = environ.re.search(r'(\${(.*?)})', value)
                while m:
                    value = re.sub(re.escape(m.group(1)), self.get_value(m.group(2)), value)
                    m = environ.re.search(r'(\${(.*?)})', value)
            return value
        except Exception as e:
            raise ImproperlyConfigured(f"Error getting configuration value {var}: {e}") from e

    def load_config(self, env_file):
        """Read a .env file into os.environ.

        If not given a path to a dotenv path, does filthy magic stack backtracking
        to find manage.py and then find the dotenv.

        http://www.wellfireinteractive.com/blog/easier-12-factor-django/

        https://gist.github.com/bennylope/2999704
        """
        # set defaults
        for key, value in DEFAULTS.items():
            self.ENVIRON.setdefault(key, str(value))
        try:
            content = Path(env_file).read_text()
        except IOError:
            warnings.warn(
                "Error reading %s - if you're not configuring your "
                "environment separately, check this." % env_file)
            return

        logger.debug('Read environment variables from: {0}'.format(env_file))

        for line in content.splitlines():
            m1 = re.match(r'\A([A-Za-z_0-9]+)=(.*)\Z', line)
            if m1:
                key, val = m1.group(1), m1.group(2)
                m2 = re.match(r"\A'(.*)'\Z", val)
                if m2:
                    val = m2.group(1)
                m3 = re.match(r'\A"(.*)"\Z', val)
                if m3:
                    val = re.sub(r'\\(.)', r'\1', m3.group(1))
                self.ENVIRON[key] = str(val)


    def write_env(self, env_file=None, **overrides):
        with open(env_file, 'w') as f:
            for k, v in self.scheme.items():
                f.write(f"{k}={self.ENVIRON[k]}\n")


# Env.DB_SCHEMES['psql'] = 'mercury.db.postgresql'

env = Env(
    DEBUG=bool,

    MEDIA_ROOT=str,
    STATIC_ROOT=str,

    ENABLE_SENTRY=bool,
    MERCURY_PLUGINS_AUTOLOAD=bool,

    EMAIL_USE_TLS=bool,
    EMAIL_HOST=str,
    EMAIL_HOST_USER=str,
    EMAIL_HOST_PASSWORD=str,
    EMAIL_PORT=str,

    DATABASE_URL=str,

    CELERY_BROKER_URL=str,

    REDIS_CONNECTION=str,
)

env.read_env(os.environ.get('BITCASTER_CONF', DEFAULT_CONFIG))
