import click

from bitcaster.cli import global_options


@click.command()
@global_options
@click.pass_context
def reindex(ctx, **kwargs):
    try:
        from django.conf import settings
        from django.db.transaction import get_connection
        conn = get_connection()
        cursor = conn.cursor()
        update_status = f'REINDEX DATABASE {settings.DATABASES["default"]["NAME"]};'
        cursor.execute(update_status)
        update_status = f'REINDEX SYSTEM {settings.DATABASES["default"]["NAME"]};'
        cursor.execute(update_status)

    except Exception as e:
        click.echo(str(e))
        ctx.exit(1)
