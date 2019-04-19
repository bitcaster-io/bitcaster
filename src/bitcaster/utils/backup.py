import json
from pathlib import Path

from django.apps import apps
from django.core.management.color import no_style
from django.db.models import ManyToManyField
from django.db.transaction import atomic
from django_regex.utils import RegexList
from sentry_sdk import capture_exception

from bitcaster.utils.json import Decoder, Encoder

DATA = ['user',
        'organization',
        'organizationmember',
        'organizationgroup',
        'application',
        'applicationteam',
        'channel',
        'event',
        'message',
        'monitor',
        'address',
        'addressassignment',
        'applicationtriggerkey',
        'subscription',
        ]
IGNORE = RegexList([r'auth\.permission', r'auth\.group'])

POP_FIELDS = ['version', 'last_modifed_date']

SECTIONS = ['options'] + DATA


def get_all_models():
    from django.apps import apps

    ret = [f'bitcaster.{n}' for n in DATA]
    for model_name in DATA:
        model = apps.get_model(f'bitcaster.{model_name}')

        m2m_attrs = [getattr(model, f.name) for f in model._meta.get_fields() if isinstance(f, ManyToManyField)]
        for m2m_attr in m2m_attrs:
            rel = m2m_attr.rel
            name = f'{rel.model._meta.app_label}.{rel.model._meta.model_name}'
            if name in IGNORE:
                continue
            # if name not in ret:
            #     ret.append(name)
            if not m2m_attr.rel.through._meta.auto_created:
                name = f'{rel.through._meta.app_label}.{rel.through._meta.model_name}'
                if name not in ret:  # pragma: no cover
                    ret.append(name)
    return ret


def backup_data(filename, echo=None):
    from constance import config, settings as sett
    # from django.apps import apps

    data = {'options': [(key, getattr(config, key)) for key, value in
                        sett.CONFIG.items()],
            }
    ALL_MODELS = get_all_models()

    for model_name in ALL_MODELS:
        data[model_name] = {'__data__': [], '__m2m__': {}}
        echo(f'backup...{model_name}')
        model = apps.get_model(model_name)
        data[model_name]['__data__'] = list(model.objects.all().values())
        m2ms = [f for f in model._meta.get_fields() if isinstance(f, ManyToManyField)]
        for m2m in m2ms:
            m2m_attr = getattr(model, m2m.name)
            if m2m_attr.rel.through._meta.auto_created:
                data[model_name]['__m2m__'][m2m.name] = list(
                    model.objects.filter(**{f'{m2m.name}__isnull': False}).values('id', m2m.name))
        json.dumps(data, cls=Encoder)

    output = Path(filename)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(data, cls=Encoder))
    echo(f'Configuration saved to {output.absolute()}')
    return output


def restore_data(filename, echo, overwrite=True, ignore_errors=False, reindex=True,
                 selection=None, reset_cryptography=False):
    from django.apps import apps
    import constance.settings
    from constance import config

    input_file = Path(filename)
    echo(f'Using backup {input_file.absolute()}')
    data = json.loads(input_file.read_text(), cls=Decoder)
    if not selection:
        selection = ['options'] + get_all_models()
    else:
        selection = ['bitcaster.%s' % name for name in selection]

    with atomic():
        if 'options' in selection:
            echo(f'restore...options')
            for key, value in data['options']:
                try:
                    _type = constance.settings.CONFIG[key][2]
                    if _type is bool:
                        value = str(value).lower() in ['1', 'true', 't']
                    elif isinstance(_type, str):
                        value = str(value)
                    else:
                        value = _type(value)
                    setattr(config, key, value)
                except Exception:
                    capture_exception()
                    raise Exception('%s=%s' % (key, value))

        ALL_MODELS = get_all_models()
        if reset_cryptography:
            from bitcaster.models import User, Channel
            User.objects.update(storage={})
            Channel.objects.update(config={})

        for model_name in ALL_MODELS:
            if model_name in selection:
                model = apps.get_model(model_name)
                try:
                    model_data = data[model_name]
                except KeyError:
                    echo(f'skipping...{model_name} no data exists', color='red')
                    continue
                echo(f'restore...{model_name}')
                for record in model_data['__data__']:
                    try:
                        pk = record.pop('id')
                        for field_name in POP_FIELDS:
                            record.pop(field_name, None)
                        if overwrite:
                            model.objects.update_or_create(id=pk, defaults=record)
                        else:
                            model.objects.get_or_create(id=pk, defaults=record)
                    except Exception as e:
                        echo('Error restoring %s' % model_name)
                        echo('ERROR: %s' % type(e))
                        echo(record)
                        # io = StringIO()
                        # traceback.print_exc(file=io)
                        # io.seek(0)
                        # echo(io.read())
                        if not ignore_errors:
                            raise
                # # ManyToMany
                for m2m_field_name, m2m_records in data[model_name]['__m2m__'].items():
                    m2m_field = model._meta.get_field(m2m_field_name)
                    related_model = m2m_field.related_model
                    for record in m2m_records:
                        parent = model.objects.get(pk=record['id'])
                        m2m_attr = getattr(parent, m2m_field_name)
                        related = related_model.objects.get(pk=record[m2m_field_name])
                        m2m_attr.add(related)
    if reindex:
        reindex_db()

    from bitcaster.models import AgentMetaData
    from bitcaster.models import DispatcherMetaData

    AgentMetaData.objects.inspect()
    DispatcherMetaData.objects.inspect()


def reindex_db():
    from django.conf import settings
    from django.db.transaction import get_connection
    conn = get_connection()
    cursor = conn.cursor()
    statements = []
    for app_name in ['bitcaster', 'social_django', 'constance']:
        app = apps.get_app_config(app_name)
        models = app.get_models(include_auto_created=True)
        stmts = conn.ops.sequence_reset_sql(no_style(), models)
        statements.extend(stmts)
    clause = ''.join(statements)
    if clause:
        cursor.execute(clause)

    update_status = f'REINDEX DATABASE {settings.DATABASES["default"]["NAME"]};'
    cursor.execute(update_status)
    update_status = f'REINDEX SYSTEM {settings.DATABASES["default"]["NAME"]};'
    cursor.execute(update_status)
