import click
from django.core.cache import caches

from bitcaster.cli import need_setup


def get_all_keys():
    from bitcaster.utils.locks import get_all_locks
    return get_all_locks()


@click.group()
@click.pass_context
@need_setup
def locks(ctx):
    pass


@locks.command()
@click.pass_context
@need_setup
def list(ctx):
    keys = get_all_keys()
    for i, key in keys.items():
        click.echo('%3s - %s' % (i, key))


@locks.command()
@click.argument('name')
@click.argument('value', default='1')
@click.pass_context
@need_setup
def add(ctx, name, value):
    lock = caches['lock']
    lock.set(name, value)


@locks.command()
@click.argument('name', nargs=1, required=False)
@click.pass_context
@need_setup
def rm(ctx, name):
    confirm = True
    if not name:
        keys = get_all_keys()
        for i, key in keys.items():
            click.echo('%3s - %s' % (i, key))
        selection = click.prompt('Choose lock to remove', type=int)
        name = keys[selection]
    else:
        confirm = click.confirm('Remove lock %s' % name)

    if confirm:
        lock = caches['lock']
        ret = lock.delete(name)
        if ret == 1:
            click.secho('%s Success' % name, fg='green')
        else:
            click.secho('%s Not found' % name, fg='yellow')
