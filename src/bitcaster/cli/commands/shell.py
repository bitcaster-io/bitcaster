import click
from django.apps import apps

import bitcaster
from bitcaster.cli import need_setup


def auto_import_objects():
    from django.conf import settings
    from bitcaster.config.environ import env
    to_load = {'settings': settings,
               'env': env}
    app_config = apps.get_app_config('bitcaster')
    for model in app_config.get_models():
        to_load[f"{model.__name__}"] = model

    click.echo(click.style("# Imported objects", fg='green'))
    click.echo(click.style(", ".join(to_load.keys()), fg='green'))
    return to_load


@click.command()
@need_setup
def shell(**kwargs):
    from IPython import start_ipython
    click.echo(click.style(f"Bitcaster shell {bitcaster.VERSION}", fg='yellow'))
    imported_objects = auto_import_objects()
    start_ipython(argv=['--autocall', '2',
                        '--term-title',
                        '--no-banner',
                        '--quiet', '--pprint'],
                  exec_lines=['%load_ext autoreload', '%autoreload 2'],
                  user_ns=imported_objects)
