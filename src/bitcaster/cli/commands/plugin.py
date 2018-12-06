import os
import re
import sys
from pathlib import Path

import click

import bitcaster
from bitcaster.cli import need_setup
from bitcaster.utils.reflect import package_name


def is_valid_name(name):
    name_char_blacklist_regexp = re.compile(r'[a-z-]*\d*$')
    return name_char_blacklist_regexp.match(name)


def cook(input_dir, output_dir, context=None, overwrite=True):
    from cookiecutter.generate import generate_files
    generate_files(
        repo_dir=input_dir,
        context=context,
        output_dir=output_dir,
        overwrite_if_exists=overwrite
    )


@click.group()
def plugin(**kwargs):
    os.environ['BITCASTER_PLUGINS_AUTOLOAD'] = 'False'
    pass


@plugin.command(name="list")
@need_setup
def _list(**kwargs):
    # need_setup(lambda : True)()
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
    from pip._internal import main as pipmain
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
        pipmain(["uninstall", r[0].project_name, '--yes'])


@plugin.command()
@click.argument('name', required=False)
@click.option('--from-dir', '-d', default=None, type=click.Path())
@click.option('--recursive', '-r', default=False, is_flag=True)
@click.option('--prompt/--no-input', default=True, is_flag=True,
              help='Do not prompt for parameters')
@need_setup
def install(name, prompt, recursive, from_dir, **kwargs):
    from pip._internal import main as pipmain
    if from_dir:
        if recursive:
            for root, subdirs, files in os.walk(from_dir):
                if os.path.exists(os.path.join(root, 'setup.py')):
                    click.echo(f"Found plugin in {root}")
                    pipmain(["install", "-q", "--ignore-installed", root])

        else:
            os.chdir(from_dir)
            pipmain(["install", '.'])


@plugin.command(name="new")
@click.argument('plugin_name')
@click.option('--author', prompt=True, )
@click.option('--license', prompt=True, default='MIT')
@click.option('--version', prompt=True, default='0.1')
@click.option('--description', prompt=True, )
@click.option('--overwrite', '-o', is_flag=True)
@click.option('-d', '--directory', prompt=True,
              default=str(Path(bitcaster.__file__).parent.parent.parent / 'plugins'))
def new_plugin(plugin_name, directory, overwrite, **options):
    name = plugin_name.lower()
    description = options['description']
    if not is_valid_name(name):
        click.echo("Invalid package name %s" % name)
        sys.exit(1)
    base_dir = Path(bitcaster.__file__).parent / '_plugin_template'
    package_name = "bitcaster_" + name.replace('-', '_')
    classname = str(name).title().replace('-', '').replace('Oauth', 'OAuth')

    context = {'cookiecutter': {'name': name,
                                'package_name': package_name,
                                'classname': classname,
                                'description': description}
               }
    context['cookiecutter'].update(options)
    cook(str(base_dir), directory, context, overwrite=overwrite)

    click.echo('%s plugin structure was succesfully created.' % name)
    click.echo(directory)
