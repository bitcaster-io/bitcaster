import re
import urllib
from functools import lru_cache
from pathlib import Path

import click

from bitcaster.config.environ import DEFAULTS


def generate_secret_key():
    from django.utils.crypto import get_random_string
    chars = u'abcdefghijklmnopqrstuvwxyz0123456789!@#%^&*(-_=+)'
    return get_random_string(50, chars)


class AddressParamType(click.ParamType):
    name = 'address'

    def convert(self, value, param, ctx):
        try:
            host, port = value.split(':', 1)
            int(port)
            return value
        except (ValueError, AssertionError):
            self.fail(
                click.style(
                    f'{value} is not a vlid address. Please use <host>:<port>',
                    fg='red'))


Address = AddressParamType()


class RedisUrlParamType(click.ParamType):
    name = 'url'

    def convert(self, value, param, ctx):
        try:
            url = urllib.parse.urlparse(value)
            assert url.scheme == 'redis'
            assert url.hostname
            assert url.port
            assert url.path
            return value
        except (ValueError, AssertionError):
            self.fail(
                click.style(
                    f'{value} is not a redis url. Please use redis://<hostname>:<port>/<database>',
                    fg='red'))


RedisURL = RedisUrlParamType()


def read_current_env(param):
    ctx = click.get_current_context()
    env = ctx.obj['env']
    return env(param) or DEFAULTS.get(param)[1]


@lru_cache(1)
def get_database_url_param():
    ctx = click.get_current_context()
    env = ctx.obj['env']

    rex = re.compile(r"psql://(?P<user>.*):(?P<password>.*)@(?P<host>.*):(?P<port>[0-9]+)/(?P<database>.*)")
    try:
        m = rex.match(env('DATABASE_URL'))
        return m.groupdict()
    except TypeError:
        return {'host': 'localhost',
                'port': 5432,
                'user': 'postgres',
                'password': '',
                'database': 'bitcaster'}


@click.command()
@click.option('--debug',
              default=lambda: read_current_env('DEBUG'),
              is_flag=True)
@click.option('--sentry-dsn',
              default=lambda: read_current_env('SENTRY_DSN'))
@click.option('--media-root',
              default=lambda: read_current_env('MEDIA_ROOT'),
              type=click.Path(file_okay=False))
@click.option('--static-root',
              default=lambda: read_current_env('STATIC_ROOT'),
              type=click.Path(file_okay=False))
@click.option('--redis-cache-url',
              default=lambda: read_current_env('REDIS_CACHE_URL'),
              type=RedisURL)
@click.option('--redis-lock-url',
              default=lambda: read_current_env('REDIS_LOCK_URL'),
              type=RedisURL)
@click.option('--celery-broker-url',
              default=lambda: read_current_env('CELERY_BROKER_URL'),
              type=RedisURL)
@click.option('--redis-constance-url',
              default=lambda: read_current_env('REDIS_CONSTANCE_URL'),
              type=RedisURL)
@click.option('--database-address',
              default=lambda: "{0[host]}:{0[port]}".format(get_database_url_param()),
              type=Address)
@click.option('--database-user',
              default=lambda: get_database_url_param()["user"])
@click.option('--database-password',
              default=lambda: get_database_url_param()["password"])
@click.option('--database-name',
              default=lambda: get_database_url_param()["database"])
@click.option('--organization',
              default=lambda: read_current_env('ORGANIZATION'))
@click.option('-p', '--prompt-all',
              default=False,
              help='Prompt for any argument even if it has default value',
              is_flag=True)
@click.option('--prompt/--no-input',
              default=True,
              help='Do not prompt for parameters',
              is_flag=True)
@click.option('--write/--dry-run',
              default=True,
              help='Do not prompt for parameters',
              is_flag=True)
@click.pass_context
def configure(ctx, prompt, prompt_all, write, **kwargs):
    cfg_file = Path(ctx.obj['config'])
    env = ctx.obj['env']

    if prompt:
        for opt in ctx.command.params:
            if opt.name not in ['prompt', 'prompt_all', 'write']:
                if prompt_all or not kwargs.get(opt.name):
                    prompt = opt.name.replace('_', ' ').capitalize()

                    v = click.prompt(prompt,
                                     default=opt.get_default(ctx),
                                     value_proc=lambda x: opt.process_value(ctx, x))
                    kwargs[opt.name] = v

    kwargs["database_url"] = "psql://{database_user}:{database_password}@{database_address}/{database_name}".format(
        **kwargs)
    kwargs["enable_sentry"] = bool(kwargs['sentry_dsn'])
    kwargs["plugins_autoload"] = True
    kwargs["secret_key"] = generate_secret_key()

    for key, value in env.scheme.items():
        env.ENVIRON[key] = str(kwargs.get(key.lower(), ''))
    if write:
        env.write_env(cfg_file)
    else:
        for key, __ in env.scheme.items():
            value = str(kwargs.get(key.lower(), ''))
            click.echo(f"{key:20} {value}")
    from constance import config
    config.ON_PREMISE = True
