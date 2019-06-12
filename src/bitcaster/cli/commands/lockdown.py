import click
from click import Context

from bitcaster.cli import need_setup


@click.group()
@click.pass_context
@need_setup
def lockdown(ctx: Context):
    pass
    from bitcaster import system
    ctx.obj['system'] = system


@lockdown.command()
@click.pass_context
def now(ctx):
    ctx.obj['system'].stop()


@lockdown.command()
@click.pass_context
def status(ctx):
    if ctx.obj['system'].running():
        click.secho('Bitcaster is running', fg='green')
    else:
        click.secho('Bitcaster stopped', fg='red')


@lockdown.command()
@click.pass_context
def remove(ctx):
    ctx.obj['system'].restart()
