import click

from bitcaster.cli import need_setup


def get_monitors():
    from bitcaster.models import Monitor
    return {int(i): m for i, m in enumerate(Monitor.objects.order_by('name'))}


@click.group()
def monitor():
    'Run a service.'


@monitor.command()
@need_setup
def list():
    click.echo('Registered monitors:')
    for i, m in get_monitors().items():
        click.echo('%3s - %s' % (i, m.name))


@monitor.command()
@click.argument('name', nargs=1, required=False, metavar='MONITOR')
@need_setup
def run(name):
    confirm = True
    if name.isdigit():
        keys = get_monitors()
        name = keys[int(name)]

    if not name:
        keys = get_monitors()
        for i, key in keys.items():
            click.echo('%3s - %s' % (i, key.name))
        selection = click.prompt('Choose monitor to run', type=int)
        name = keys[selection]
    else:
        confirm = click.confirm('Running monitor %s?' % name)

    if confirm:
        name.check_and_run()
