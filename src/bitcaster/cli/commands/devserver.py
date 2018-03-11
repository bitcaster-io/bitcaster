# -*- coding: utf-8 -*-
import logging
import os
import sys

import click

from bitcaster.cli.utils import Address, LogLeveParamType
from bitcaster.services.http import HTTPServer

logger = logging.getLogger(__name__)


@click.command()
@click.option('--bind', '-b', default='localhost:8000', type=Address,
              help='Bind address.')
@click.option('--workers', '-w', default=1,
              help='The number of worker processes for handling requests.')
@click.option('--upgrade', default=False, is_flag=True,
              help='Upgrade before starting.')
@click.option('--debug', '-d', default=False, is_flag=True,
              help='Start server in debug mode')
@click.option('--webpack', default=False, is_flag=True,
              help='Start webpack watch mode')
@click.option('--no-input', default=False, is_flag=True,
              help='Do not prompt the user for input of any kind.')
@click.option('--autoreload/--noreload/', default=True, is_flag=True,
              help='Restart server on server change')
@click.option('--loglevel', '-l', default='debug',
              type=LogLeveParamType(),
              help=('Logging level, choose between DEBUG, INFO, WARNING,'
                    ' ERROR, CRITICAL, or FATAL.'))
@click.option('--logfile', default=None,
              help='logfile')
def devserver(bind, workers, autoreload, debug,
              webpack, logfile, **kwargs):
    host, port = bind.split(":")
    webpack_proc = None

    if debug:
        os.environ['BITCASTER_DEBUG'] = 'True'
        os.environ['CELERY_ALWAYS_EAGER'] = 'True'

    if webpack:
        import subprocess

        webpack_proc = subprocess.Popen(['webpack', '--mode', 'development', '--watch'],
                             stdout=sys.stdout,
                             stderr=sys.stderr)

    HTTPServer(host=host,
               port=port,
               debug=debug,
               workers=workers,
               reload=autoreload).run()

    if webpack_proc:
        webpack_proc.kill()
