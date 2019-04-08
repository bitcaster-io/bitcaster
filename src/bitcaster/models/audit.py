from enum import IntEnum

from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils import timezone


class AuditLogEntry(models.Model):
    class Event(IntEnum):
        MEMBER_LOGIN = -1
        MEMBER_LOGOUT = -2

        MEMBER_EDIT = 1
        MEMBER_UPDATE_ADDRESS = 2
        MEMBER_DELETE_ADDRESS = 3
        MEMBER_ADD_ADDRESS = 4

        MEMBER_ADD_ASSIGNMENT = 5
        MEMBER_CHANGE_ASSIGNMENT = 6

        MEMBER_UPDATE_PROFILE = 7
        MEMBER_SUBSCRIBE_EVENT = 8
        MEMBER_DELETE_SUBSCRIPTION = 9
        MEMBER_TOGGLE_SUBSCRIPTION = 10

        @classmethod
        def get_by_value(cls, v):
            try:
                label = ([val for val in cls if val == v][0]).name
                return label.replace('_', ' ').title()
            except IndexError:
                return 'N/A'

    organization = models.ForeignKey('bitcaster.Organization',
                                     null=True,
                                     on_delete=models.CASCADE)
    actor = models.ForeignKey('bitcaster.User', models.SET_NULL,
                              related_name='audit_actors', null=True, blank=True)
    actor_label = models.CharField(max_length=64, null=True, blank=True)

    target_object = models.PositiveIntegerField(null=True)
    target_label = models.CharField(max_length=300, null=True, blank=True)

    event = models.IntegerField(choices=[(tag.value, tag.name) for tag in Event])

    ip_address = models.GenericIPAddressField(null=True, unpack_ipv4=True)
    data = JSONField(null=True)
    datetime = models.DateTimeField(default=timezone.now)

    def get_message(self):
        msg = self.Event.get_by_value(self.event)
        return '{msg} '.format(msg=msg)

    def save(self, *args, **kwargs):
        if not self.actor_label:
            if self.actor:
                self.actor_label = self.actor.display_name
        super(AuditLogEntry, self).save(*args, **kwargs)

    def get_actor_name(self):
        if self.actor:
            return self.actor.display_name
        return self.actor_label
