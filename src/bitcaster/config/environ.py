# -*- coding: utf-8 -*-
import logging

from environ import ImproperlyConfigured, environ, re

from bitcaster.config import DEFAULTS

logger = logging.getLogger(__name__)


class Env(environ.Env):
    def __init__(self, prefix, **scheme):
        self.scheme = scheme
        self.prefix = prefix or ''

    def __getattr__(self, var):
        # t = f"{self.prefix}{var}"
        return self.get_value(var)

    def get_value(self, var, cast=None, default=environ.Env.NOTSET,  # noqa: C901
                  parse_default=False, raw=False):
        """Return value for given environment variable.

                :param var: Name of variable.
                :param cast: Type to cast return value as.
                :param default: If var not present in environ, return this instead.
                :param parse_default: force to parse default..

                :returns: Value from environment or default (if set)
                """

        if raw:
            env_var = var
        else:
            env_var = f'{self.prefix}{var}'

        # logger.debug(f"get '{env_var}' casted as '{cast}' with default '{default}'")

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
                    default = var_info[1]
            else:
                if not cast:
                    cast = var_info

        try:
            value = self.ENVIRON[env_var]
        except KeyError:
            if default is self.NOTSET:
                error_msg = f'Set the {env_var} environment variable'
                raise ImproperlyConfigured(error_msg)

            value = default

        # Resolve any proxied values
        if hasattr(value, 'startswith') and '${' in value:
            m = environ.re.search(r'(\${(.*?)})', value)
            while m:
                value = re.sub(re.escape(m.group(1)), self.get_value(m.group(2), raw=True), value)
                m = environ.re.search(r'(\${(.*?)})', value)

        if value != default or (parse_default and value):
            value = self.parse_value(value, cast)

        logger.debug(f"get '{var}' returns '{value}'")
        return value

    # def load_config(self, env_file: str = None, check_exists: bool = False):
    #     """Read a .env file into os.environ.
    #
    #     If not given a path to a dotenv path, does filthy magic stack backtracking
    #     to find manage.py and then find the dotenv.
    #
    #     http://www.wellfireinteractive.com/blog/easier-12-factor-django/
    #
    #     https://gist.github.com/bennylope/2999704
    #     """
    #     if env_file is None:
    #         env_file = os.environ.get('BITCASTER_CONF', DEFAULT_CONFIG)
    #     logger.debug(f'Read environment variables from: {env_file}')
    #     if not os.path.exists(env_file):
    #         if check_exists:
    #             raise ImproperlyConfigured(f"Configuration file '{env_file}' does not exists or cannot be read")
    #
    #         return
    #     # set defaults
    #     for key, value in DEFAULTS.items():
    #         self.ENVIRON.setdefault(f'{self.prefix}{key}', str(value[1]))
    #
    #     try:
    #         content = Path(env_file).read_text()
    #     except IOError:
    #         raise ImproperlyConfigured(f'{env_file} not found')
    #
    #     for line in content.splitlines():
    #         m1 = re.match(r'\A([A-Za-z_0-9]+)=(.*)\Z', line)
    #         if m1:
    #             key, val = m1.group(1), m1.group(2)
    #             m2 = re.match(r"\A'(.*)'\Z", val)
    #             if m2:
    #                 val = m2.group(1)
    #             m3 = re.match(r'\A"(.*)"\Z', val)
    #             if m3:
    #                 val = re.sub(r'\\(.)', r'\1', m3.group(1))
    #             self.ENVIRON[f'{self.prefix}{key}'] = str(val)

    # def write_env(self, env_file=None, **overrides):
    #     with open(env_file, 'w') as f:
    #         for k, v in self.scheme.items():
    #             f.write(f'{k}={self.ENVIRON[k]}\n')


env = Env('BITCASTER_', **DEFAULTS)
# env.load_config(os.environ.get('BITCASTER_CONF', DEFAULT_CONFIG), False)
