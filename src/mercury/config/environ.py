# -*- coding: utf-8 -*-
from pathlib import Path

from environ import ImproperlyConfigured, environ, os, re, warnings

from mercury import logging
from mercury.config import DEFAULT_CONFIG

logger = logging.getLogger(__name__)

DEFAULTS = dict(
    DEBUG=(bool, False),
    SECRET_KEY=(str, ''),
    MEDIA_ROOT=(str, str(Path('~/.bitcaster/media').expanduser())),
    STATIC_ROOT=(str, str(Path('~/.bitcaster/static').expanduser())),
    #
    ENABLE_SENTRY=(bool, False),
    SENTRY_DSN=(str, ''),
    PLUGINS_AUTOLOAD=(bool, False),
    DATABASE_URL=(str, 'psql://postgres:@127.0.0.1:5432/mercury'),
    REDIS_CACHE_URL=(str, 'redis://localhost:6379/0'),
    REDIS_LOCK_URL=(str, 'redis://localhost:6379/1'),
    CELERY_BROKER_URL=(str, 'redis://localhost:6379/2'),
    REDIS_CONSTANCE_URL=(str, 'redis://localhost:6379/3'),

)


class Env(environ.Env):
    def __init__(self, prefix, **scheme):
        self.scheme = scheme
        self.prefix = prefix or ''

    def get_value(self, var, cast=None, default=environ.Env.NOTSET, parse_default=False):
        """Return value for given environment variable.

                :param var: Name of variable.
                :param cast: Type to cast return value as.
                :param default: If var not present in environ, return this instead.
                :param parse_default: force to parse default..

                :returns: Value from environment or default (if set)
                """

        logger.debug("get '{0}' casted as '{1}' with default '{2}'".format(
            var, cast, default
        ))

        env_var = f"{self.prefix}{var}"
        if var in self.scheme:
            var_info = self.scheme[var]

            try:
                has_default = len(var_info) == 2
            except TypeError:
                has_default = False

            if has_default:
                if not cast:
                    cast = var_info[0]

                if default is self.NOTSET:
                    try:
                        default = var_info[1]
                    except IndexError:
                        pass
            else:
                if not cast:
                    cast = var_info

        try:
            value = self.ENVIRON[env_var]
        except KeyError:
            if default is self.NOTSET:
                error_msg = "Set the {0} environment variable".format(var)
                raise ImproperlyConfigured(error_msg)

            value = default

        # Resolve any proxied values
        if hasattr(value, 'startswith') and '${' in value:
            m = environ.re.search(r'(\${(.*?)})', value)
            while m:
                value = re.sub(re.escape(m.group(1)), self.get_value(m.group(2)), value)
                m = environ.re.search(r'(\${(.*?)})', value)

        if value != default or (parse_default and value):
            value = self.parse_value(value, cast)

        return value

        # try:
        #     var = f"{self.prefix}{var}"
        #     value = super().get_value(var, cast, default, parse_default)
        #     if hasattr(value, 'startswith') and '${' in value:
        #         m = environ.re.search(r'(\${(.*?)})', value)
        #         while m:
        #             value = re.sub(re.escape(m.group(1)), self.get_value(m.group(2)), value)
        #             m = environ.re.search(r'(\${(.*?)})', value)
        #     return value
        # except Exception as e:
        #     raise ImproperlyConfigured(f"Error getting configuration value {var}: {e}") from e

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

# env = Env('BITCASTER_', **dict((k, type(v)) for k, v in DEFAULTS.items()))
env = Env('BITCASTER_', **DEFAULTS)

env.read_env(os.environ.get('BITCASTER_CONF', DEFAULT_CONFIG))
