import click

from bitcaster.cli import need_setup


@click.group()
@click.pass_context
@need_setup
def locks(ctx):
    pass


@click.group()
@click.pass_context
@need_setup
def list(ctx):
    pass
