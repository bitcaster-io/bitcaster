import os
from pathlib import Path

import click

from bitcaster.config.environ import env


@click.command()
@click.option('--prompt/--no-input', default=True, is_flag=True,
              help='Do not prompt for parameters')
@click.option('--migrate/--no-migrate', default=True, is_flag=True,
              help='Do not prompt for parameters')
@click.pass_context
def upgrade(ctx, prompt, migrate, **kwargs):
    try:
        from django.core.management import execute_from_command_line

        if prompt:
            extra = []
        else:
            extra = ['--no-input']

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
                    click.echo(f"Create {_dir} '{target}'")
                    target.mkdir(parents=True)
        if migrate:
            execute_from_command_line(argv=['manage', 'migrate'] + extra)
        execute_from_command_line(argv=['manage', 'collectstatic'] + extra)
    except Exception as e:
        click.echo(str(e))
        ctx.abort()
