import json
from pathlib import Path

import click
from django.db.models import ManyToManyField
from django.db.transaction import atomic

from bitcaster.cli import need_setup
from bitcaster.cli.commands.option import option_set
from bitcaster.utils.json import Decoder, Encoder

DATA = ['user',
        'monitormetadata', 'dispatchermetadata',
        'organization',
        'application',
        'channel',
        'organizationmember', 'address', 'addressassignment',
        'event',
        'message',
        'applicationtriggerkey',
        ]
POP_FIELDS = ['version', 'last_modifed_date']

SECTIONS = ['options'] + DATA


@click.command()
@click.option('--filename', default='bitcaster.json', type=click.Path())
@click.pass_context
@need_setup
def backup(ctx, filename):
    from constance import config, settings as sett
    from django.apps import apps
    try:
        data = {'options': [(key, getattr(config, key)) for key, value in
                            sett.CONFIG.items()],
                }
        for model_name in DATA:
            data[model_name] = {'__data__': [], '__m2m__': {}}
            click.echo(f'backup...{model_name}')
            model = apps.get_model(f'bitcaster.{model_name}')
            data[model_name]['__data__'] = list(model.objects.all().values())
            m2ms = [f.name for f in model._meta.get_fields() if isinstance(f, ManyToManyField)]
            for m2m in m2ms:
                m2m_attr = getattr(model, m2m)
                if not m2m_attr.through:
                    data[model_name]['__m2m__'][m2m] = list(
                        model.objects.filter(**{f'{m2m}__isnull': False}).values('id', m2m))
            json.dumps(data, cls=Encoder)

        output = Path(filename)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(data, cls=Encoder))
        click.echo(f'Configuration saved to {output.absolute()}')
    except Exception as e:
        click.echo(str(e))
        ctx.abort()


@click.command()  # noqa: C901
@click.option('--filename', default='bitcaster.json', type=click.Path())
@click.option('-o', '--only', 'selection', default=None, multiple=True, type=click.Choice(SECTIONS))
@click.option('-w', '--overwrite', 'overwrite', default=False, is_flag=True)
@click.option('-i', '--ignore-errors', default=False, is_flag=True,
              help='Try to continueon error')
@click.pass_context
@need_setup
def restore(ctx, filename, overwrite, ignore_errors, selection):
    from django.apps import apps

    input_file = Path(filename)
    click.echo(f'Using backup {input_file.absolute()}')
    data = json.loads(input_file.read_text(), cls=Decoder)
    if not selection:
        selection = SECTIONS
    with atomic():
        if 'options' in selection:
            for key, value in data['options']:
                ctx.invoke(option_set, name=key, value=value)
        for model_name in DATA:
            if model_name in selection:
                model = apps.get_model(f'bitcaster.{model_name}')
                click.echo(f'restore...{model_name}')
                for record in data[model_name]['__data__']:
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
                # ManyToMany
                for m2m_field_name, m2m_records in data[model_name]['__m2m__'].items():
                    m2m_field = model._meta.get_field(m2m_field_name)
                    m2m_attr = getattr(model, m2m_field_name)
                    related_model = m2m_field.related_model
                    for record in m2m_records:
                        parent = model.objects.get(pk=record['id'])
                        m2m_attr = getattr(parent, m2m_field_name)
                        related = related_model.objects.get(pk=record[m2m_field_name])
                        m2m_attr.add(related)
