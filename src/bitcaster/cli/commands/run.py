import sys
from multiprocessing import cpu_count

import click
from celery.signals import celeryd_after_setup

from bitcaster.cli import need_setup
from bitcaster.utils.reflect import fqn


class QueueSetType(click.ParamType):
    name = 'text'

    def convert(self, value, param, ctx):
        if value is None:
            return None
        queues = set()
        for queue in value.split(','):
            queues.add(queue)
        return frozenset(queues)


QueueSet = QueueSetType()


@click.group()
def run():
    'Run a service.'


@run.command()
@click.option('--queues', '-Q', type=QueueSet,
              help=('List of queues to enable for this worker, separated by '
                    'comma. By default all configured queues are enabled. '
                    'Example: -Q video,image'
                    ))
@click.option('--exclude-queues', '-X', type=QueueSet)
@click.option('--concurrency', '-c', default=cpu_count(),
              help=('Number of child processes processing the queue. The '
                    'default is the number of CPUs available on your '
                    'system.'
                    ))
@click.option('--logfile', '-f', help='Path to log file. If no logfile is specified, stderr is used.')
@click.option('-l', '--loglevel', default='error')
@click.option('--quiet', '-q', is_flag=True, default=False)
@click.option('--no-color', is_flag=True, default=False)
@click.option('--without-gossip', is_flag=True, default=False)
@click.option('--without-mingle', is_flag=True, default=False)
@click.option('--without-heartbeat', is_flag=True, default=False)
@click.option('--max-tasks-per-child', default=10000)
@click.option('--pidfile', default='celery.pid')
@click.option('--prune', is_flag=True, default=False)
@need_setup
def worker(**options):
    'Run background worker instance.'
    from django.conf import settings
    if settings.CELERY_TASK_ALWAYS_EAGER:
        raise click.ClickException(
            'Disable CELERY_TASK_ALWAYS_EAGER in your settings file to spawn workers.'
        )

    from bitcaster.celery import app
    if not options['queues']:
        @celeryd_after_setup.connect
        def setup_queues(instance, conf, **kwargs):
            from bitcaster.models import DispatcherMetaData
            for d in DispatcherMetaData.objects.all():
                # instance.app.control.add_consumer(fqn(d.handler), reply=True)
                instance.app.amqp.queues.select_add(fqn(d.handler))

    worker = app.Worker(pool_cls='processes', **options)
    worker.start()
    try:
        sys.exit(worker.exitcode)
    except AttributeError:
        # `worker.exitcode` was added in a newer version of Celery:
        # https://github.com/celery/celery/commit/dc28e8a5
        # so this is an attempt to be forwards compatible
        pass


@run.command()
@click.option('--pidfile', help=('Optional file used to store the process pid. The '
                                 'program will not start if this file already exists and '
                                 'the pid is still alive.'
                                 )
              )
@click.option('--logfile', '-f',
              help=('Path to log file. If no logfile is specified, stderr is used.'))
@click.option('-l', '--loglevel', default='error')
@click.option('--quiet', '-q', is_flag=True, default=False)
@click.option('--no-color', is_flag=True, default=False)
@click.option('--without-gossip', is_flag=True, default=False)
@click.option('--without-mingle', is_flag=True, default=False)
@click.option('--without-heartbeat', is_flag=True, default=False)
@need_setup
def beat(**options):
    'Run periodic task dispatcher.'
    from django.conf import settings
    if settings.CELERY_TASK_ALWAYS_EAGER:
        raise click.ClickException(
            'Disable CELERY_TASK_ALWAYS_EAGER in your settings file to spawn workers.'
        )

    from bitcaster.celery import app
    app.Beat(**options).run()

#
# @run.command()
# @click.option('--port', default=25, type=int)
# @click.option('--hostname', default='localhost')
# @need_setup
# def smtp(hostname, port):
#     from smtpd import SMTPServer
#     import asyncore
#     foo = SMTPServer((hostname, port), None)
#     try:
#         asyncore.loop()
#     except KeyboardInterrupt:
#         pass
