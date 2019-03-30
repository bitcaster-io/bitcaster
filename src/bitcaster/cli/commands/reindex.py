import click
from django.apps import apps
from django.core.management.color import no_style

from bitcaster.cli import global_options, need_setup


@click.command()
@global_options
@click.pass_context
@need_setup
def reindex(ctx, **kwargs):
    try:
        from django.conf import settings
        from django.db.transaction import get_connection
        conn = get_connection()
        cursor = conn.cursor()
        statements = []
        for app_name in ['bitcaster', 'social_django', 'constance']:
            app = apps.get_app_config(app_name)
            models = app.get_models(include_auto_created=True)
            stmts = conn.ops.sequence_reset_sql(no_style(), models)
            statements.extend(stmts)
        clause = ''.join(statements)
        if clause:
            cursor.execute(clause)

        update_status = f'REINDEX DATABASE {settings.DATABASES["default"]["NAME"]};'
        cursor.execute(update_status)
        update_status = f'REINDEX SYSTEM {settings.DATABASES["default"]["NAME"]};'
        cursor.execute(update_status)
    except Exception as e:
        click.echo(str(e))
        ctx.exit(1)
