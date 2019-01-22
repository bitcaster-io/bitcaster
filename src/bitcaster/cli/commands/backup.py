import json
from pathlib import Path

import click
from django.db.transaction import atomic

from bitcaster.cli import need_setup
from bitcaster.cli.commands.option import option_set
from bitcaster.utils.json import Decoder, Encoder

DATA = ['organization', 'channel',
        'user', 'organizationmember', 'address',
        'application', 'event', 'message', 'applicationtriggerkey',
        ]
POP_FIELDS = ['version', 'last_modifed_date']


@click.command()
@click.option('--filename',
              default='bitcaster.json',
              type=click.Path())
@click.pass_context
@need_setup
def backup(ctx, filename):
    from constance import config, settings as sett
    from django.apps import apps
    try:
        data = {'options': [(key, getattr(config, key)) for key, value in
                            sett.CONFIG.items()]
                }
        for model_name in DATA:
            click.echo(f'backup...{model_name}')
            model = apps.get_model(f'bitcaster.{model_name}')
            data[model_name] = list(model.objects.all().values())
            json.dumps(data, cls=Encoder)

        output = Path(filename)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(data, cls=Encoder))
        click.echo(f'Configuration saved to {output.absolute()}')
    except Exception as e:
        click.echo(str(e))
        ctx.abort()


@click.command()
@click.option('--filename', default='bitcaster.json', type=click.Path())
@click.option('-o', '--overwrite', 'overwrite', default=False, is_flag=True)
@click.option('-i', '--ignore-errors', default=False, is_flag=True,
              help='Try to continueon error')
@click.pass_context
@need_setup
def restore(ctx, filename, overwrite, ignore_errors):
    from django.apps import apps

    input_file = Path(filename)
    click.echo(f'Using backup {input_file.absolute()}')
    data = json.loads(input_file.read_text(), cls=Decoder)

    with atomic():
        for key, value in data['options']:
            ctx.invoke(option_set, name=key, value=value)

        for model_name in DATA:
            model = apps.get_model(f'bitcaster.{model_name}')
            click.echo(f'restore...{model_name}')
            for record in data[model_name]:
                try:
                    pk = record.pop('id')
                    for field_name in POP_FIELDS:
                        record.pop(field_name, None)
                    if overwrite:
                        model.objects.update_or_create(id=pk, defaults=record)
                    else:
                        model.objects.get_or_create(id=pk, defaults=record)
                except Exception as e:
                    click.echo(str(e))
                    click.echo(model_name)
                    click.echo(record)
                    if not ignore_errors:
                        ctx.abort()
