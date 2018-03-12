import click
import os
import pip
import sys

from bitcaster.cli import need_setup
from bitcaster.utils.reflect import package_name


@click.group()
@click.pass_context
def plugin(ctx, **kwargs):
    pass


@plugin.command(name="list")
@need_setup
def _list(**kwargs):
    from bitcaster.dispatchers.registry import dispatcher_registry
    for entry in sorted(dispatcher_registry,
                        key=lambda e: e.name):
        core = "*" if entry.__core__ else " "
        click.echo(f"{entry.name:20} {core} {entry.fqn}")


@plugin.command()
@click.argument('name')
@click.option('--prompt/--no-input', default=True, is_flag=True,
              help='Do not prompt for parameters')
@need_setup
def uninstall(name, prompt, **kwargs):
    from bitcaster.dispatchers.registry import dispatcher_registry
    import pkg_resources  # part of setuptools
    found = [entry for entry in dispatcher_registry if entry.name.lower() == name.lower()]
    if not found:
        click.echo(f"Plugin '{name}' not found")
        sys.exit(1)
    found = found[0]
    if found.__core__:
        click.echo(f"Plugin '{name}' is a core component and cannot be removed")
        sys.exit(1)
    r = pkg_resources.require(package_name(found.__module__))
    if click.prompt(f"Uninstall plugin {found.name}?"):
        pip.main(["uninstall", r[0].project_name, '--yes'])


@plugin.command()
@click.argument('name', required=False)
@click.option('--from-dir', '-d', default=None, type=click.Path())
@click.option('--recursive', '-r', default=False, is_flag=True)
@click.option('--prompt/--no-input', default=True, is_flag=True,
              help='Do not prompt for parameters')
@need_setup
def install(name, prompt, recursive, from_dir, **kwargs):
    os.environ['BITCASTER_PLUGINS_AUTOLOAD'] = 'False'
    if from_dir:
        if recursive:
            for root, subdirs, files in os.walk(from_dir):
                if os.path.exists(os.path.join(root, 'setup.py')):
                    pip.main(["install", root])

        else:
            os.chdir(from_dir)
            pip.main(["install", '.'])
