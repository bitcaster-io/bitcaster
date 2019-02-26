import os
from pathlib import Path

import click

from bitcaster.cli import global_options


@click.command()
@global_options
@click.option('--prompt/--no-input', default=True, is_flag=True,
              help='Do not prompt for parameters')
@click.option('--migrate/--no-migrate', default=True, is_flag=True,
              help='Run database migrations')
@click.option('--static/--no-static', default=True, is_flag=True,
              help='Collect static assets')
@click.pass_context
def upgrade(ctx, prompt, migrate, static, verbose, **kwargs):
    try:
        from django.conf import settings
        from django.db.transaction import get_connection
        from django.core.management import execute_from_command_line
        from bitcaster.config.environ import env

        if prompt:
            extra = []
        else:
            extra = ['--no-input']

        extra.extend(['-v', str(verbose)])

        os.environ['BITCASTER_DEBUG'] = 'True'
        os.environ['BITCASTER_PLUGINS_AUTOLOAD'] = 'False'
        for _dir in ('MEDIA_ROOT', 'STATIC_ROOT'):
            target = Path(env.str(_dir))
            if not target.exists():
                if prompt:
                    ok = click.prompt(f"{_dir} set to '{target}' but it does not exists. Create it now?")
                else:
                    ok = True
                if ok:
                    if verbose > 0:
                        click.echo(f"Create {_dir} '{target}'")
                    target.mkdir(parents=True)
        # if static:
        #     execute_from_command_line(argv=['manage', 'collectstatic'] + extra)
        if migrate:
            execute_from_command_line(argv=['manage', 'migrate'] + extra)
        conn = get_connection()
        cursor = conn.cursor()
        update_status = f'REINDEX DATABASE {settings.DATABASES["default"]["NAME"]};'
        cursor.execute(update_status)

    except Exception as e:
        click.echo(str(e))
        ctx.abort()
