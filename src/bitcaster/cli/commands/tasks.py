import click

from bitcaster.cli import need_setup


def get_tasks():
    from bitcaster.celery import app
    return {str(i): name for i, name in enumerate(sorted(app.tasks.keys()))}


@click.group()
def tasks():
    'Run a service.'


@tasks.command()
@need_setup
def list():
    click.echo('Registered tasks:')
    for i, name in get_tasks().items():
        click.echo('%3s - %s' % (i, name))


@tasks.command()
@click.argument('name', metavar='TASK')
@click.argument('args', nargs=-1, required=False)
@click.option('--sync', is_flag=True)
@need_setup
def run(name, args, sync):
    from bitcaster.celery import app
    if name.isdigit():
        name = get_tasks()[name]
    elif '.' not in name:
        name = next(filter(lambda n: n.endswith(name), get_tasks().values()))

    task = app.tasks[name]
    click.echo('Running %s' % name)
    parsed_args = []
    for a in args:
        if a.startswith('[') and a.endswith(']'):
            parsed_args.append((a[1:-1]).split(','))
        else:
            parsed_args.append(a)
    try:
        if sync:
            ret = task(*parsed_args)
            click.echo(ret)
        else:
            ret = task.delay()
    except Exception as e:
        click.secho(str(e), fg='red')
