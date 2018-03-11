import click
import os


@click.command()
@click.option('--prompt/--no-input',
              default=True,
              help='Do not prompt for parameters',
              is_flag=True)
@click.pass_context
def upgrade(ctx, prompt, **kwargs):
    try:
        from django.core.management import execute_from_command_line
        if prompt:
            extra = []
        else:
            extra = ['--no-input']
        os.environ['BITCASTER_DEBUG'] = 'True'

        execute_from_command_line(argv=['manage', 'migrate'] + extra)
        execute_from_command_line(argv=['manage', 'collectstatic'] + extra)
    except Exception as e:
        click.echo(str(e))
        ctx.abort()
