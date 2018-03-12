import os
import sys
from functools import update_wrapper
from pathlib import Path

import click
from setproctitle import setproctitle
from strategy_field.utils import import_by_name

import bitcaster
from bitcaster.config import DEFAULT_CONFIG
from bitcaster.config.environ import env

_global_options = [
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


def configure():
    try:
        import django
        django.setup()
    except Exception as e:
        click.echo(f"Error configuring environment. "
                   f"Run 'bitcaster configure' first: ({e})")
        sys.exit(1)


def need_setup(f):
    def new_func(*args, **kwargs):
        configure()
        return f(*args, **kwargs)
    return update_wrapper(new_func, f)


@click.group()
@global_options
@click.version_option(version=bitcaster.get_full_version())
@click.pass_context
def cli(ctx, config, **kwargs):
    """Bitcaster is cross-platform .

    The configuration file is looked up in the `~/.bitcaster/conf` config
    directory but this can be overridden with the `BITCASTER_CONF`
    environment variable or be explicitly provided through the
    `--config` parameter.
    """
    config = Path(config).expanduser().absolute()
    filepath = str(config)
    os.environ['BITCASTER_CONF'] = filepath
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bitcaster.config.settings.default')

    if config.exists():
        # raise click.ClickException(f"config file {filepath} does not exists.")
        # cfg_file.parent.mkdir(mode=0o770, parents=True, exist_ok=True)
        # cfg_file.touch(mode=0o660)
        env.load_config(str(config))
    ctx.obj = {'env': env,
               'config': filepath}
    click.echo("Configuration file: {}".format(ctx.obj['config']))


cli.add_command(import_by_name('bitcaster.cli.commands.check.check'))
cli.add_command(import_by_name('bitcaster.cli.commands.configure.configure'))
cli.add_command(import_by_name('bitcaster.cli.commands.upgrade.upgrade'))
cli.add_command(import_by_name('bitcaster.cli.commands.option.option'))
# cli.add_command(import_by_name('bitcaster.cli.commands.devserver.devserver'))
cli.add_command(import_by_name('bitcaster.cli.commands.createuser.createuser'))
cli.add_command(import_by_name('bitcaster.cli.commands.backup.backup'))
cli.add_command(import_by_name('bitcaster.cli.commands.backup.restore'))
cli.add_command(import_by_name('bitcaster.cli.commands.start.start'))
cli.add_command(import_by_name('bitcaster.cli.commands.devserver.devserver'))
cli.add_command(import_by_name('bitcaster.cli.commands.plugin.plugin'))


def main():  # pragma: no cover
    setproctitle('{} {}'.format(bitcaster.NAME, " ".join(sys.argv[1:])))
    cli(prog_name=bitcaster.NAME, obj={}, max_content_width=100)
