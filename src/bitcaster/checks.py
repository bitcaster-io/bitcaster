import base64
import logging
from pathlib import Path

import redis
from cryptography.fernet import Fernet, InvalidToken
from django.contrib.auth import get_user_model
from django.core.cache import caches
from django.core.checks import Error, register
from django.db import OperationalError, ProgrammingError, connection

from bitcaster.config import settings
from bitcaster.config.environ import env
from bitcaster.exceptions import PluginValidationError
from bitcaster.models import AgentMetaData, Channel, DispatcherMetaData

logger = logging.getLogger(__name__)


@register()
def check_settings(*args, **kwargs):
    errors = []
    for i, dir in enumerate(['MEDIA_ROOT', 'STATIC_ROOT']):
        value = getattr(settings, dir)
        if not value or not Path(value).is_dir():
            errors.append(
                Error(
                    "%s '%s' does not exists" % (dir, getattr(settings, dir)),
                    hint='check your BITCASTER_%s environment variable' % dir,
                    obj=None,
                    id='bitcaster.C00%s' % i
                )
            )
    return errors


@register(deploy=True)
def check_channel_configuration(*args, **kwargs):
    errors = []
    invalid = []
    for record in Channel.objects.filter(enabled=True).only('handler'):
        try:
            record.handler.validate_configuration(record.handler.config, True)
        except PluginValidationError:
            invalid.append(record.pk)
            errors.append(
                Error(
                    'Channel %s has been disabled' % record,
                    hint='check channel configuration',
                    obj=record.pk,
                    id='bitcaster.E001',
                )
            )

    # Channel.objects.filter(id__in=invalid).update(enabled=False)
    return errors


@register()
def check_dispatchers(*args, **kwargs):
    try:
        DispatcherMetaData.objects.inspect()
        AgentMetaData.objects.inspect()
    except ProgrammingError:  # this happens in ./manage.py migrate
        pass
    return []


@register()
def check_tsdb(*args, **kwargs):
    try:
        from bitcaster.tsdb.api import stats
        stats.client.dbsize()
    except Exception as e:
        return [Error('Unable to contact REDIS_TSDB_URL',
                      hint=str(e),
                      obj=None,
                      id='bitcaster.TS001',
                      )]
    return []


@register(deploy=True)
def check(*args, **kwargs):
    errors = []
    try:
        from django.core.cache import cache
        cache.set('cache_connection_test', 'true', 1)
    except redis.exceptions.ConnectionError:
        errors.append(
            Error(
                'Unable to contact Redis',
                hint='check your redis configuration',
                obj=None,
                id='bitcaster.E001',
            )
        )
    try:
        connection.cursor()
    except OperationalError:  # pragma: no cover
        errors.append(
            Error(
                'Database Error',
                hint='check your database configuration',
                obj=None,
                id='bitcaster.E002',
            )
        )

    try:
        caches['default'].set('check', 1)
    except Exception:
        errors.append(
            Error(
                "Unable to contact cache backend at '%s'" % env('REDIS_CACHE_URL'),
                hint='check your database configuration',
                obj=None,
                id='bitcaster.E003',
            )
        )

    try:
        caches['lock'].set('check', 1)
    except Exception as e:
        errors.append(
            Error(
                "Unable to contact lock backend at '%s'" % env('REDIS_LOCK_URL'),
                hint=str(e),
                obj=None,
                id='bitcaster.E004',
            )
        )
    return errors


@register(deploy=True)
def check_dirs(*args, **kwargs):
    errors = []
    for _dir in ('MEDIA_ROOT', 'STATIC_ROOT'):
        if not Path(env(_dir)).exists():
            errors.append(
                Error(
                    f"{_dir} '{Path(env(_dir))}' does not exists",
                    hint='check your configuration',
                    obj=None,
                    id='bitcaster.E005',
                )
            )
    return errors


@register(deploy=True)
def check_fernets(*args, **kwargs):
    errors = []
    try:
        UserModel = get_user_model()
        UserModel.objects.first()
    except InvalidToken:
        errors.append(
            Error(
                'Unable to decrypt database',
                hint='SECRET_KEY/FERNET_KEYS seems changed. Cannot decrypt existing data',
                obj=None,
                id='bitcaster.E006',
            )
        )
    except ProgrammingError:  # pragma: no cover
        # check fails if first setup, because migrations have not ran
        pass

    try:
        Fernet(base64.urlsafe_b64encode(settings.FERNET_KEYS[0].encode()[:32]))
    except Exception as e:
        errors.append(Error(
            str(e),
            hint='check your BITCASTER_FERNET_KEYS environment variable',
            obj=None,
            id='bitcaster.E007'
        ))

    return errors
