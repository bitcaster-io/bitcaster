import os
# from functools import lru_cache
#
# import logging
# import re
import urllib

import click

#
# from bitcaster.config import DEFAULTS
from bitcaster.exceptions import ImproperlyConfigured


#
# logger = logging.getLogger(__name__)
#
# #
# # def generate_secret_key():
# #     from django.utils.crypto import get_random_string
# #     chars = u'abcdefghijklmnopqrstuvwxyz0123456789!@#%^&*(-_=+)'
# #     return get_random_string(50, chars)
#
#
# class AddressParamType(click.ParamType):
#     name = 'address'
#
#     def convert(self, value, param, ctx):
#         try:
#             host, port = value.split(':', 1)
#             int(port)
#             return value
#         except (ValueError, AssertionError):
#             self.fail(
#                 click.style(
#                     f'{value} is not a valid address. Please use <host>:<port>',
#                     fg='red'))
#
#
# Address = AddressParamType()
#
class VerbosityParamType(click.ParamType):
    name = 'address'

    def __init__(self) -> None:
        self.quit = False

    def convert(self, value, param, ctx):
        self.total = value
        if param.name == 'quit':
            self.quit = True
        if self.quit:
            value = 0
        return int(value)


Verbosity = VerbosityParamType()

# class RedisUrlParamType(click.ParamType):
#     name = 'url'
#
#     def convert(self, value, param, ctx):
#         try:
#             url = urllib.parse.urlparse(value)
#             assert url.scheme == 'redis'
#             assert url.hostname
#             assert url.port
#             # assert url.path
#             return value
#         except (ValueError, AssertionError):
#             self.fail(
#                 click.style(
#                     f'{value} is not a redis url. Please use redis://<hostname>:<port>/<database>',
#                     fg='red'))
#
#
# RedisURL = RedisUrlParamType()
#
#
# def read_current_env(param):
#     ctx = click.get_current_context()
#     env = ctx.obj['env']
#     return env(param) or DEFAULTS.get(param)[1]
#
#
# @lru_cache(1)
# def get_database_url_param():
#     ctx = click.get_current_context()
#     env = ctx.obj['env']
#
#     rex = re.compile(r'psql://(?P<user>.*):(?P<password>.*)@(?P<host>.*):(?P<port>[0-9]+)/(?P<database>.*)')
#     try:
#         m = rex.match(env('DATABASE_URL'))
#         return m.groupdict()
#     except TypeError:
#         return {'host': 'localhost',
#                 'port': 5432,
#                 'user': 'postgres',
#                 'password': '',
#                 'database': 'bitcaster'}
#
#
LOG_LEVELS = ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL', 'FATAL')


class CaseInsensitiveChoice(click.Choice):
    def convert(self, value, param, ctx):
        self.choices = [choice.upper() for choice in self.choices]
        return super().convert(value.upper(), param, ctx)


class LogLevelParamType(CaseInsensitiveChoice):

    def __init__(self, choices=LOG_LEVELS):
        super().__init__(choices)

    def convert(self, value, param, ctx):
        value = super().convert(value.upper(), param, ctx)
        os.environ['BITCASTER_LOG_LEVEL'] = value.upper()
        return value


ERROR_LEVELS = ('CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG')


class ErrorLeveParamType(CaseInsensitiveChoice):

    def __init__(self, choices=ERROR_LEVELS):
        super().__init__(choices)


def wait_for_service(address, timeout=30, caption='', stdout=None, sleep=0):
    import socket
    import time

    if isinstance(address, (list, tuple)):
        ip, port = address
    else:
        url = urllib.parse.urlparse(address)
        ip = url.hostname
        port = url.port

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    start = time.time()
    end = start + timeout
    while True:
        if stdout:
            stdout.write(caption)
            stdout.flush()
        try:
            s.connect((ip, port))
            s.close()
            break
        except socket.error:
            time.sleep(0.5)
        except Exception as e:
            raise ImproperlyConfigured(f'Error checking {address}. {e}')
        if time.time() > end:
            raise TimeoutError
    stdout.write(caption + 'OK\n')
    time.sleep(sleep)
