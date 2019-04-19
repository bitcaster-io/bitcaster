import os
import sys
import time

import click
# from django.core.checks import Warning
from django.db import OperationalError

from bitcaster.cli import global_options
from bitcaster.cli.utils import ErrorLeveParamType, wait_for_service
from bitcaster.exceptions import ImproperlyConfigured


def checkdb(wait=True, timeout=60, debug=False, connection='default'):
    from django.db import connections
    elapsed = 0
    retcode = 0
    try:
        click.echo(f'Checking db connnection {connection}...')
        conn = connections[connection]
        while True:
            try:
                conn = conn.cursor()
            except OperationalError as e:
                if wait and elapsed < timeout:
                    sys.stdout.write('.' * elapsed)
                    sys.stdout.flush()
                    time.sleep(1)
                    elapsed += 1
                else:
                    sys.stderr.write(f"\nDatabase on {conn.settings_dict['HOST']}:{conn.settings_dict['PORT']} "
                                     f'is not available after {elapsed} secs')
                    if debug:
                        sys.stderr.write(f'Error is: {e}')
                    retcode = 1
                    break
            else:
                sys.stdout.write(f'Connection {connection} successful\n')
                break
    except KeyboardInterrupt:  # pragma: no-cover
        sys.stdout.write('Interrupted')
    return retcode


@click.command()  # noqa
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
              help='wait until required services are ready')
@click.option('--timeout', default=60, type=int,
              help='Timeout for waiting for services')
@click.option('--sleep', default=5, type=int,
              help='Sleep time waiting for services')
@click.pass_context
def check(ctx, debug, deploy, tags, list_tags, fail_level, wait_services,
          timeout, sleep, verbose, **kwargs):
    if debug:
        os.environ['BITCASTER_DEBUG'] = 'True'
        os.environ['BITCASTER_PLUGINS_AUTOLOAD'] = 'False'

    # os.environ['BITCASTER_CONF'] = ctx.obj['config']

    from bitcaster.config.environ import env
    # env.load_config()

    if deploy:
        wait_services = True
    if wait_services:
        for service, name in [('DATABASE_URL', 'database'),
                              ('CELERY_BROKER_URL', 'celery broker'),
                              ('REDIS_CACHE_URL', 'cache server'),
                              ('REDIS_LOCK_URL', 'lock server')]:
            try:
                sys.stdout.write(f'Check {name}')
                sys.stdout.flush()
                wait_for_service(env(service),
                                 caption='.',
                                 sleep=sleep,
                                 timeout=timeout,
                                 stdout=sys.stdout if verbose > 0 else None)
            except TimeoutError:
                click.echo(f"Timeout checking {name}: '{env(service)}'")
                sys.exit(1)
            except ImproperlyConfigured as e:
                click.echo(f"Error checking {name}: '{env(service)}'")
                click.echo(e)
                sys.exit(1)
        checkdb(wait=True, timeout=timeout)

    extra = ['--fail-level', fail_level, ]

    if deploy:
        extra = ['--deploy']
    if list_tags:
        extra = ['--list_tags']
    try:
        from django.core.management import execute_from_command_line
        import django
        django.setup()
        execute_from_command_line(argv=['manage'] + ['check'] + extra)
    except Exception as e:
        click.echo(str(e))
        ctx.abort()
    #
    # if deploy:
    #     try:
    #         click.echo(f"Checking cryptography keys")
    #         checkfernet()
    #     except ImproperlyConfigured:
    #         click.echo(f"Error in cryptography keys")
    #         ctx.abort()
    #     except Exception as e:
    #         click.echo(str(e))
    #         ctx.abort()
