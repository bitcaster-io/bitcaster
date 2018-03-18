# -*- coding: utf-8 -*-
import logging
from collections import namedtuple
from enum import Enum

from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils import timezone
from django.utils.deconstruct import deconstructible

from bitcaster.utils.wsgi import get_client_ip

logger = logging.getLogger(__name__)

AuditLogEntryTuple = namedtuple("aaa", "id,label,verbose")


@deconstructible
class AuditEvent(Enum):
    MEMBER_INVITE = (1, "member:invite",
                     "{0.actor} invited member {0.data[email]} to {0.organization} as {0.data[role]}")

    MEMBER_ACCEPT = (2, "member:accept",
                     "{0.actor} accepted invitation from {0.data[invited_by]} to {0.organization} as {0.data[role]}")

    def __init__(self, value, label, description):
        self.int = value
        self.label = label
        self.description = description

    def verbose(self, data):
        return self.description.format(**data)

    def __eq__(self, other):
        return self.int == other

    def __gt__(self, other):
        return self.int > other

    def __lt__(self, other):
        return self.int < other

    @classmethod
    def as_choices(cls):
        return [(a.int, a.label) for a in cls]


class AuditEventField(models.IntegerField):
    def __init__(self, verbose_name=None, name=None, db_index=False, serialize=True,
                 choices=AuditEvent.as_choices(),
                 default=None,
                 help_text='', db_column=None, db_tablespace=None, validators=(), error_messages=None):
        super().__init__(verbose_name=verbose_name, name=name,
                         choices=choices,
                         db_index=db_index, serialize=serialize, default=default,
                         help_text=help_text,
                         db_column=db_column, db_tablespace=db_tablespace, validators=validators,
                         error_messages=error_messages)

    def get_prep_value(self, value):
        return super().get_prep_value(value.int)

    def value_to_string(self, obj):
        """
        Return a string value of this field from the passed obj.
        This is used by the serialization framework.
        """
        return str(self.value_from_object(obj).int)


class AuditLogEntry(models.Model):
    organization = models.ForeignKey('bitcaster.Organization',
                                     blank=True, null=True,
                                     on_delete=models.CASCADE)
    application = models.ForeignKey('bitcaster.Application',
                                    blank=True, null=True,
                                    on_delete=models.CASCADE)
    actor = models.CharField(max_length=64, null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             blank=True, null=True,
                             on_delete=models.CASCADE)
    event = AuditEventField()
    ip_address = models.GenericIPAddressField(null=True, unpack_ipv4=True)
    data = JSONField()
    datetime = models.DateTimeField(default=timezone.now)

    def __str__(self):
        description = next((a for a in AuditEvent if a.int == self.event)).description
        return description.format(self)

    class Meta:
        ordering = ('-datetime',)
        get_latest_by = 'datetime'


def audit_log(request, event, logger=None, organization=None, application=None, **kwargs):
    user = request.user if request.user.is_authenticated else None
    logger = logging.getLogger('bitcaster.audit') if logger is None else logger
    actor = user.email

    entry = AuditLogEntry(
        actor=actor,
        user=user,
        organization=organization,
        application=application,
        event=event,
        ip_address=get_client_ip(request),
        data=kwargs
    )
    entry.save()
    if logger:
        logger.info(str(entry))

    return entry
