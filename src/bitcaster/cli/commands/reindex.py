import click

from bitcaster.cli import global_options, need_setup


@click.command()
@global_options
@click.pass_context
@need_setup
def reindex(ctx, **kwargs):
    from bitcaster.utils.backup import reindex_db

    try:
        reindex_db()
    except Exception as e:
        click.echo(str(e))
        ctx.exit(1)
