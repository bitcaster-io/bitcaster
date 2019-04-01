import click

from bitcaster.cli import need_setup
from bitcaster.utils.backup import SECTIONS


@click.command()
@click.option('--filename', default='bitcaster.json', type=click.Path())
@click.pass_context
@need_setup
def backup(ctx, filename):
    from bitcaster.utils.backup import backup_data

    try:
        backup_data(filename, echo=click.echo)
    except Exception as e:
        click.echo(str(e))
        ctx.abort()


@click.command()  # noqa: C901
@click.option('--filename', default='bitcaster.json', type=click.Path())
@click.option('--reindex/--no-reindex', default=False)
@click.option('-o', '--only', 'selection', default=None, multiple=True, type=click.Choice(SECTIONS))
@click.option('-w', '--overwrite', 'overwrite', default=False, is_flag=True)
@click.option('-i', '--ignore-errors', default=False, is_flag=True,
              help='Try to continueon error')
@click.pass_context
@need_setup
def restore(ctx, filename, overwrite, ignore_errors, selection, reindex):
    from bitcaster.utils.backup import restore_data

    try:
        restore_data(filename, echo=click.echo, overwrite=overwrite,
                     ignore_errors=ignore_errors, selection=selection,
                     reindex=reindex)
    except Exception as e:
        click.echo(str(e))
        ctx.abort()

    # except Exception as e:
    #     raise
    #     click.echo(e, color='red')
    #     ctx.exit(1)
