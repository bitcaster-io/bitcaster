# -*- coding: utf-8 -*-
"""
mercury / utils
~~~~~~~~~~~~~~~~~

:copyright: (c) 2018 Stefano Apostolico, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

import logging
import re
import urllib
from functools import lru_cache

import click

from bitcaster.config.environ import DEFAULTS

logger = logging.getLogger(__name__)


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
