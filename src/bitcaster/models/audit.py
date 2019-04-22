from enum import Enum

from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils import timezone

MESSAGES = {}


class AuditLogEntry(models.Model):
    class AuditEvent(Enum):
        MEMBER_LOGIN = 'MEMBER_LOGIN'
        MEMBER_LOGOUT = 'MEMBER_LOGOUT'

        MEMBER_EDIT = 'MEMBER_EDIT'
        MEMBER_UPDATE_ADDRESS = 'MEMBER_UPDATE_ADDRESS'
        MEMBER_DELETE_ADDRESS = 'MEMBER_DELETE_ADDRESS'
        MEMBER_ADD_ADDRESS = 'MEMBER_ADD_ADDRESS'

        INVITATION_CREATED = 'INVITATION_CREATED'
        INVITATION_SENT = 'INVITATION_SENT'
        INVITATION_ACCEPTED = 'INVITATION_ACCEPTED'

        MEMBER_ADD_ASSIGNMENT = 'MEMBER_ADD_ASSIGNMENT'
        MEMBER_CHANGE_ASSIGNMENT = 'MEMBER_CHANGE_ASSIGNMENT'
        MEMBER_DELETE_ASSIGNMENT = 'MEMBER_DELETE_ASSIGNMENT'

        MEMBER_UPDATE_PROFILE = 'MEMBER_UPDATE_PROFILE'
        MEMBER_SUBSCRIBE_EVENT = 'MEMBER_SUBSCRIBE_EVENT'
        MEMBER_DELETE_SUBSCRIPTION = 'MEMBER_DELETE_SUBSCRIPTION'
        MEMBER_TOGGLE_SUBSCRIPTION = 'MEMBER_TOGGLE_SUBSCRIPTION'
        MEMBER_VALIDATE_ADDRESS = 'MEMBER_VALIDATE_ADDRESS'

        MEMBERSHIP_CREATED = 'MEMBERSHIP_CREATED'

        SUBSCRIPTION_ERROR = 'SUBSCRIPTION_ERROR'

        @classmethod
        def get_by_value(cls, v):
            try:
                label = ([val for val in cls if val == v][0]).name
                return label.replace('_', ' ').title()
            except IndexError:
                return 'N/A (%s)' % v

    AUDITEVENT_CHOICES = [(tag.value, tag.name) for tag in AuditEvent]

    organization = models.ForeignKey('bitcaster.Organization',
                                     blank=True, null=True,
                                     on_delete=models.CASCADE)
    actor = models.ForeignKey('bitcaster.User', models.SET_NULL,
                              related_name='audit_actors', null=True, blank=True)
    actor_label = models.CharField(max_length=64, null=True, blank=True)

    target_object = models.PositiveIntegerField(blank=True, null=True)
    target_label = models.CharField(max_length=300, null=True, blank=True)

    event = models.CharField(choices=AUDITEVENT_CHOICES,
                             max_length=100)

    ip_address = models.GenericIPAddressField(blank=True, null=True, unpack_ipv4=True)
    data = JSONField(blank=True, null=True)
    timestamp = models.DateTimeField(default=timezone.now)

    def get_message(self):
        msg = self.AuditEvent.get_by_value(self.event)
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
