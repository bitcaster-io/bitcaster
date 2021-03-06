import click

from bitcaster.cli import need_setup
from bitcaster.utils.backup import SECTIONS


@click.command()
@click.option('-f', '--filename', default='bitcaster.json', type=click.Path())
@click.option('-o', '--overwrite', is_flag=True, default=False)
@click.pass_context
@need_setup
def backup(ctx, filename, overwrite):
    from bitcaster.utils.backup import backup_data

    try:
        backup_data(filename, echo=click.echo, overwrite_exists=overwrite)
    except Exception as e:
        click.echo(str(e))
        ctx.abort()


@click.command()  # noqa: C901
@click.option('--filename', default='bitcaster.json', type=click.Path())
@click.option('--reindex/--no-reindex', default=True)
@click.option('-o', '--only', 'selection', default=None, multiple=True, type=click.Choice(SECTIONS))
@click.option('-w', '--overwrite', 'overwrite', default=False, is_flag=True)
@click.option('-i', '--ignore-errors', default=False, is_flag=True, help='Try to continue on error')
@click.option('--reset-cryptography', default=False, is_flag=True, help='encrypth records')
@click.option('--zap', default=False, is_flag=True, help='empty all tables before restore')
@click.pass_context
@need_setup
def restore(ctx, filename, overwrite, ignore_errors, selection, reindex, reset_cryptography, zap):
    from bitcaster.utils.backup import restore_data

    try:
        restore_data(filename, echo=click.echo, overwrite=overwrite,
                     ignore_errors=ignore_errors, selection=selection,
                     reindex=reindex, reset_cryptography=reset_cryptography,
                     zap=zap)
    except Exception as e:
        click.echo(str(e))
        ctx.abort()

    # except Exception as e:
    #     raise
    #     click.echo(e, color='red')
    #     ctx.exit(1)
