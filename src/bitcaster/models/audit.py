# -*- coding: utf-8 -*-
import logging

from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext as _

from bitcaster.db.fields import EnumField
from bitcaster.models import Organization, Application

logger = logging.getLogger(__name__)


class AuditLogEntryEvent(EnumField):
    MEMBER_INVITE = (1, "{actor} invited member {data['email']} as data['role']")


    @classmethod
    def as_choices(cls):
        return sorted([(int(cls.MEMBER_INVITE[0]), _('Active')),
                       (int(cls.M), _('Deprecated')),
                       (int(cls.PENDING_DELETION), _('Pending Deletion')),
                       (int(cls.DELETION_IN_PROGRESS), _('Deletion in Progress')),
                       ])


class AuditEventField(models.IntegerField):
    def __init__(self, verbose_name=None, name=None, db_index=False, serialize=True,
                 choices=AuditLogEntryEvent.as_choices(),
                 default=None,
                 help_text='', db_column=None, db_tablespace=None, validators=(), error_messages=None):
        super().__init__(verbose_name=verbose_name, name=name,
                         choices=choices,
                         db_index=db_index, serialize=serialize, default=default,
                         help_text=help_text,
                         db_column=db_column, db_tablespace=db_tablespace, validators=validators,
                         error_messages=error_messages)

    def get_prep_value(self, value):
        return super().get_prep_value(int(value))

    def value_to_string(self, obj):
        """
        Return a string value of this field from the passed obj.
        This is used by the serialization framework.
        """
        return str(int(self.value_from_object(obj)))


class AuditLogEntry(models.Model):
    organization = models.ForeignKey(Organization,
                                     on_delete=models.CASCADE)
    application = models.ForeignKey(Application,
                                    on_delete=models.CASCADE)
    actor = models.CharField(max_length=64, null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             blank=True, null=True,
                             on_delete=models.CASCADE)
    event = AuditEventField()
    ip_address = models.GenericIPAddressField(null=True, unpack_ipv4=True)
    data = JSONField()
    datetime = models.DateTimeField(default=timezone.now)

# if self.event == AuditLogEntryEvent.MEMBER_INVITE:
#     return 'invited member %s' % (self.data['email'],)
