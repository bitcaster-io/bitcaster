import os
import sys

import click

from bitcaster.cli import global_options
from bitcaster.cli.utils import ErrorLeveParamType, wait_for_service


@click.command()
@global_options
@click.option('--debug', '-d', default=False, is_flag=True,
              help='debug mode')
@click.option('--list-tags', default=False, is_flag=True,
              help='List available tags.')
@click.option('--fail-level', default='ERROR',
              type=ErrorLeveParamType(),
              help='Message level that will cause the command '
                   'to exit with a non-zero status. Default is ERROR.')
@click.option('--tag', '-t', 'tags', multiple=True,
              help='Run only checks labeled with given tag.')
@click.option('--deploy', default=False, is_flag=True,
              help='Check deployment settings.')
@click.option('--wait-services', default=False, is_flag=True,
              help='debug mode')
@click.option('--timeout', default=60, type=int,
              help='debug mode')
@click.option('--sleep', default=1, type=int,
              help='debug mode')
@click.pass_context
def check(ctx, debug, deploy, tags, list_tags, fail_level, wait_services,
          timeout, sleep, verbose, **kwargs):
    if debug:
        os.environ['BITCASTER_DEBUG'] = 'True'
        os.environ['BITCASTER_PLUGINS_AUTOLOAD'] = 'False'

    if wait_services:
        from bitcaster.config.environ import env
        for service, name in [('DATABASE_URL', 'database'),
                              ('CELERY_BROKER_URL', 'celery broker'),
                              ('REDIS_CACHE_URL', 'cache server'),
                              ('REDIS_LOCK_URL', 'lock server')]:
            wait_for_service(env(service),
                             caption=f"Check {name}..",
                             sleep=sleep,
                             timeout=timeout,
                             stdout=sys.stdout if verbose > 0 else None)

    extra = ['--fail-level', fail_level, ]
    if deploy:
        extra = ['--deploy']
    if list_tags:
        extra = ['--list_tags']
    try:
        from django.core.management import execute_from_command_line
        os.environ['BITCASTER_CONF'] = ctx.obj['config']

        execute_from_command_line(argv=['manage'] + ['check'] + extra)
    except Exception as e:
        click.echo(str(e))
        ctx.abort()
