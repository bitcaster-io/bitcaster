import os
import sys
from functools import update_wrapper
from pathlib import Path

import click
from strategy_field.utils import import_by_name

import bitcaster
from bitcaster.cli.utils import Verbosity
from bitcaster.config import DEFAULT_CONFIG

_global_options = [
    click.option('-v', '--verbose',
                 default=1,
                 type=Verbosity,
                 count=True),
    click.option('-q', '--quit',
                 default=0, is_flag=True, type=Verbosity),
    click.option('-c',
                 '--config',
                 default=DEFAULT_CONFIG,
                 envvar='BITCASTER_CONF',
                 help='Path to configuration directory.',
                 metavar='FILE')
]


def global_options(func):
    for option in reversed(_global_options):
        func = option(func)
    return func


_configured = False


def configure():
    try:
        import django
        django.setup()
    except Exception as e:
        click.echo(click.style(f'Error configuring environment. '
                               f"Run 'bitcaster configure' first: ({e})", fg='red'))
        sys.exit(1)


def need_setup(f):
    def new_func(*args, **kwargs):
        global _configured
        if not _configured:
            configure()
            _configured = True
        return f(*args, **kwargs)

    return update_wrapper(new_func, f)


@click.group()
@global_options
@click.version_option(version=bitcaster.VERSION)
@click.pass_context
def cli(ctx, config, verbose, **kwargs):
    config = Path(config).expanduser().absolute()
    filepath = str(config)
    os.environ['BITCASTER_CONF'] = filepath
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bitcaster.config.settings')
    from bitcaster.config.environ import env

    ctx.obj = {'env': env,
               'config': filepath}


cli.add_command(import_by_name('bitcaster.cli.commands.check.check'))
cli.add_command(import_by_name('bitcaster.cli.commands.upgrade.upgrade'))
cli.add_command(import_by_name('bitcaster.cli.commands.createuser.createuser'))
cli.add_command(import_by_name('bitcaster.cli.commands.backup.backup'))
cli.add_command(import_by_name('bitcaster.cli.commands.backup.restore'))
cli.add_command(import_by_name('bitcaster.cli.commands.reindex.reindex'))
cli.add_command(import_by_name('bitcaster.cli.commands.run.run'))
cli.add_command(import_by_name('bitcaster.cli.commands.changepassword.changepassword'))
cli.add_command(import_by_name('bitcaster.cli.commands.locks.locks'))
cli.add_command(import_by_name('bitcaster.cli.commands.tasks.tasks'))


def main():  # pragma: no cover
    os.environ['BITCASTER_LOG_LEVEL'] = 'ERROR'
    cli(prog_name=bitcaster.NAME, obj={}, max_content_width=100)
