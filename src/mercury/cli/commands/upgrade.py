import click


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
            noinput = ''
        else:
            noinput = '--no-input'
        execute_from_command_line(argv=['manage', 'collectstatic', noinput])
        execute_from_command_line(argv=['manage', 'migrate', noinput])
    except Exception as e:
        click.echo(str(e))
        ctx.abort()
