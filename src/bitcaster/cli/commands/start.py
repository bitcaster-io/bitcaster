# -*- coding: utf-8 -*-
import logging
import os
import sys

import click

from bitcaster.cli.utils import Address, LogLeveParamType
from bitcaster.services.http import HTTPServer

logger = logging.getLogger(__name__)


@click.group()
@click.pass_context
def start(ctx, **kwargs):
    pass


@start.command()
@click.option('--hostname', '-n',
              help=('Set custom hostname, e.g. \'w1.%h\'. Expands: %h'
                    '(hostname), %n (name) and %d, (domain).'))
@click.option('--queues', '-Q',
              help=('List of queues to enable for this worker, separated by '
                    'comma. By default all configured queues are enabled. '
                    'Example: -Q video,image'
                    ))
@click.option('--concurrency', '-c', default=os.cpu_count(),
              help=('Number of child processes processing the queue. The '
                    'default is the number of CPUs available on your '
                    'system.'
                    ))
@click.option('--logfile', '-f',
              help=('Path to log file. '
                    'If no logfile is specified, stderr is used.'))
@click.option('--loglevel', '-l', default='info',
              type=LogLeveParamType(),
              help=('Logging level, choose between DEBUG, INFO, WARNING,'
                    ' ERROR, CRITICAL, or FATAL.'))
@click.option('--detach', '-D', is_flag=True, default=False,
              help="Start worker as a background process.")
@click.option('--quiet', '-q', is_flag=True, default=False)
@click.option('--no-color', is_flag=True, default=False)
@click.option('--autoreload', is_flag=True, default=False,
              help='Enable autoreloading.')
@click.option('--without-gossip', is_flag=True, default=False,
              help="Don't subscribe to other workers events.")
@click.option('--without-mingle', is_flag=True, default=False,
              help="Don't synchronize with other workers at start-up.")
@click.option('--without-heartbeat', is_flag=True, default=False,
              help="Don't send event heartbeats.")
@click.option('--max-tasks-per-child', default=10000,
              help=("Maximum number of tasks a pool worker can execute "
                    "before it's terminated and replaced by a new worker."))
def workers(**options):
    "Run background worker instance."
    from django.conf import settings
    if settings.CELERY_ALWAYS_EAGER:
        raise click.ClickException(
            'Disable CELERY_ALWAYS_EAGER in your settings file to spawn workers.'
        )
    from bitcaster.celery import app
    # from celery.apps.worker import Worker
    worker = app.Worker(
        pool_cls='processes',
        **options
    )
    worker.start()
    sys.exit(worker.exitcode)


@start.command()
@click.option('--bind', '-b', default='localhost:8000', type=Address,
              help='Bind address.')
@click.option('--workers', '-w', default=4,
              help='The number of worker processes for handling requests.')
@click.option('--upgrade', default=False, is_flag=True,
              help='Upgrade before starting.')
@click.option('--debug', '-d', default=False, is_flag=True,
              help='Start server in debug mode')
@click.option('--daemonize', '-D', default=False, is_flag=True,
              help='Daemonize and exit')
@click.option('--pidfile', '-p', default=None,
              help='pidfile to')
@click.option('--noinput', default=False, is_flag=True,
              help='Do not prompt the user for input of any kind.')
@click.option('--autoreload', default=False, is_flag=True,
              help='Restart server on server change')
@click.option('--loglevel', '-l', default='info',
              type=LogLeveParamType(),
              help=('Logging level, choose between DEBUG, INFO, WARNING,'
                    ' ERROR, CRITICAL, or FATAL.'))
@click.option('--logfile', default=None,
              help='logfile')
@click.pass_context
def web(ctx, bind, daemonize, pidfile, workers, autoreload, debug, logfile, **kwargs):
    host, port = bind.split(":")
    if debug:
        os.environ['BITCASTER_DEBUG'] = 'True'

    HTTPServer(host=host,
               port=port,
               debug=debug,
               workers=workers,
               reload=autoreload,
               daemonize=daemonize,
               pidfile=pidfile).run()
