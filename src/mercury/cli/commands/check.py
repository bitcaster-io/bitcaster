import click


@click.command()
@click.pass_context
def check(ctx, **kwargs):
    click.echo("Configuration file: {}".format(ctx.obj['config']))
    try:
        from django.core.management import execute_from_command_line
        execute_from_command_line(argv=['manage'] + list(['check']))
    except Exception as e:
        click.echo(str(e))
        ctx.abort()
