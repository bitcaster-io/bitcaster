import json
from pathlib import Path

import click

from bitcaster.cli import need_setup
from bitcaster.cli.commands.option import option_set
from bitcaster.utils.json import Decoder, Encoder

DATA = ['organization', 'user', 'organizationmember', 'channel', 'application', 'event']


@click.command()
@click.option('--file',
              'filename',
              default='bitcaster.json',
              type=click.Path())
@click.pass_context
@need_setup
def backup(ctx, filename, **kwargs):
    from constance import config, settings as sett
    from django.apps import apps
    try:
        data = {'options': [(key, getattr(config, key)) for key, value in
                            sett.CONFIG.items()]
                }
        for model_name in DATA:
            model = apps.get_model(f'bitcaster.{model_name}')
            data[model_name] = list(model.objects.all().values())

        output = Path(filename)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(data, cls=Encoder))
        click.echo(f'Configuration savet to {output.absolute()}')
    except Exception as e:
        click.echo(str(e))
        ctx.abort()


@click.command()
@click.option('--file',
              'filename',
              default='bitcaster.json',
              type=click.Path())
@click.option('--overwrite',
              'overwrite',
              default=False,
              is_flag=True)
@click.pass_context
@need_setup
def restore(ctx, filename, overwrite, **kwargs):
    from django.apps import apps
    import warnings
    # DateTimeField ... received a naive datetime (2019-01-16 19:13:39.717907) while time zone support is active.
    warnings.simplefilter('ignore', RuntimeWarning, 1421)

    input = Path(filename)
    click.echo(f'Using backup {input.absolute()}')
    backup = json.loads(input.read_text(), cls=Decoder)
    for key, value in backup['options']:
        ctx.invoke(option_set,
                   name=key,
                   value=value)

    for model_name in DATA:
        model = apps.get_model(f'bitcaster.{model_name}')
        for record in backup[model_name]:
            try:
                id = record.pop('id')
                record.pop('version', None)
                model.objects.update_or_create(id=id, defaults=record)
            except Exception as e:
                click.echo(str(e))
                click.echo(model_name)
                click.echo(record)
                ctx.abort()
