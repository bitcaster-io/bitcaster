import os
import sys
from functools import update_wrapper
from pathlib import Path

import click
from setproctitle import setproctitle
from strategy_field.utils import import_by_name

import mercury
from mercury.config import DEFAULT_CONFIG
from mercury.config.environ import env

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


def need_setup(f):
    def new_func(*args, **kwargs):
        import django
        django.setup()
        return f(*args, **kwargs)
    return update_wrapper(new_func, f)


@click.group()
@global_options
@click.version_option(version=mercury.get_full_version())
@click.pass_context
def cli(ctx, config, **kwargs):
    """Bitcaster is cross-platform .

    The configuration file is looked up in the `~/.bitcaster/conf` config
    directory but this can be overridden with the `BITCASTER_CONF`
    environment variable or be explicitly provided through the
    `--config` parameter.
    """
    filepath = os.path.realpath(os.path.expanduser(config))
    os.environ['BITCASTER_CONF'] = filepath
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mercury.config.settings.default')

    cfg_file = Path(config)
    if not cfg_file.exists():
        cfg_file.parent.mkdir(mode=0o770, parents=True, exist_ok=True)
        cfg_file.touch(mode=0o660)
    env.load_config(cfg_file)
    ctx.obj = {'env': env,
               'config': filepath}


cli.add_command(import_by_name('mercury.cli.commands.check.check'))
cli.add_command(import_by_name('mercury.cli.commands.configure.configure'))
cli.add_command(import_by_name('mercury.cli.commands.upgrade.upgrade'))
cli.add_command(import_by_name('mercury.cli.commands.option.option'))
# cli.add_command(import_by_name('mercury.cli.commands.devserver.devserver'))
cli.add_command(import_by_name('mercury.cli.commands.createuser.createuser'))


def main():  # pragma: no cover
    setproctitle('{} {}'.format(mercury.NAME, " ".join(sys.argv[1:])))
    cli(prog_name=mercury.NAME, obj={}, max_content_width=100)
