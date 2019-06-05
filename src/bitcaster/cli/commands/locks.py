import click
import redis
from django.core.cache import caches

from bitcaster.cli import need_setup


@click.group()
@click.pass_context
@need_setup
def lock(ctx):
    pass


@lock.command()
@click.pass_context
@need_setup
def list(ctx):
    lock = caches['lock']
    r = redis.StrictRedis.from_url(lock._server)

    for key in r.scan_iter('*'):
        # TODO: remove me
        print(111, 'locks.py:21', key)
