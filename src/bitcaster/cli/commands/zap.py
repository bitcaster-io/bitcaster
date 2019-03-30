import click
from django.apps import apps

from bitcaster.cli import need_setup
from bitcaster.cli.commands.upgrade import upgrade


def parse_bool(value):
    return value.lower() not in ['', '0', 'false', 'f', 'n']


caster = {bool: parse_bool,
          int: parse_bool,
          }


@click.command()
@click.pass_context
@need_setup
def zap(ctx):
    from django.db import connection
    cursor = connection.cursor()
    for app_name in ['bitcaster', 'social_django', 'constance']:
        app = apps.get_app_config(app_name)
        for model in app.get_models():
            click.echo('Zapping {}'.format(model._meta.verbose_name))
            cursor.execute('TRUNCATE TABLE "{0}" CASCADE '.format(model._meta.db_table))

    ctx.invoke(upgrade)
