from enum import IntEnum

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext as _

from bitcaster.tasks.model import async

xCREATE = 1
xUPDATE = 2
xDELETE = 3
xENABLED = 4
xDISABLED = 5
xDEPRECATED = 6


class AuditEvent(IntEnum):
    MEMBER_LOGIN = 0
    MEMBER_LOGOUT = 1
    # Application - 100
    APPLICATION_CREATED = 101
    APPLICATION_UPDATED = 102
    APPLICATION_DELETED = 103
    APPLICATION_ENABLED = 104
    APPLICATION_DISABLED = 105

    # Invitations - 2xx
    INVITATION_CREATED = 201
    INVITATION_SENT = 202
    INVITATION_ACCEPTED = 203
    MEMBERSHIP_CREATED = 601

    # user - 3xx
    MEMBER_UPDATE_PROFILE = 302

    # user/address - 31x
    ADDRESS_CREATED = 311
    ADDRESS_UPDATED = 312
    ADDRESS_DELETED = 313
    ADDRESS_VERIFIED = 314

    ASSIGNMENT_CREATED = 401
    ASSIGNMENT_UPDATED = 402
    ASSIGNMENT_DELETED = 403

    SUBSCRIPTION_CREATED = 505
    SUBSCRIPTION_UPDATED = 506
    SUBSCRIPTION_DELETED = 507
    SUBSCRIPTION_ENABLED = 507
    SUBSCRIPTION_DISABLED = 507

    CHANNEL_CREATED = 801
    CHANNEL_UPDATED = 802
    CHANNEL_DELETED = 803
    CHANNEL_ENABLED = 804
    CHANNEL_DISABLED = 805
    CHANNEL_DEPRECATED = 806

    EVENT_CREATED = 901
    EVENT_UPDATED = 902
    EVENT_DELETED = 903
    EVENT_ENABLED = 904
    EVENT_DISABLED = 905
    EVENT_DEV_MODE_ON = 906
    EVENT_DEV_MODE_OFF = 907

    MONITOR_CREATED = 1001
    MONITOR_UPDATED = 1002
    MONITOR_DELETED = 1003
    MONITOR_ENABLED = 1004
    MONITOR_DISABLED = 1005
    MONITOR_TERMINATED = 1006


_CREATED = _('%(actor)s has created %(content_type)s %(target)s')
_UPDATED = _('%(actor)s has updated %(content_type)s %(target)s')
_DELETED = _('%(actor)s has deleted %(content_type)s %(target)s')
_DISABLED = _('%(actor)s disabled %(content_type)s %(target)s')
_ENABLED = _('%(actor)s enabled %(content_type)s %(target)s')
_DEPRECATED = _('%(actor)s has deprecated %(content_type)s %(target)s')

MESSAGES = {
    AuditEvent.APPLICATION_CREATED: _CREATED,
    AuditEvent.APPLICATION_UPDATED: _UPDATED,
    AuditEvent.APPLICATION_DELETED: _DELETED,
    AuditEvent.APPLICATION_ENABLED: _ENABLED,
    AuditEvent.APPLICATION_DISABLED: _DISABLED,
    AuditEvent.MEMBER_LOGIN: _('%(actor)s logged in'),
    AuditEvent.MEMBER_LOGOUT: _('%(actor)s logged out'),

    AuditEvent.INVITATION_CREATED: _("%(actor)s invited '%(target)s'"),
    AuditEvent.INVITATION_SENT: _("%(actor)s sent invitation to '%(target)s'"),
    AuditEvent.INVITATION_ACCEPTED: _('%(actor)s accepted invitation'),

    AuditEvent.MEMBER_UPDATE_PROFILE: _('%(actor)s updated profile'),
    AuditEvent.ADDRESS_UPDATED: _("%(actor)s updated address '%(target)s'"),
    AuditEvent.ADDRESS_DELETED: _("%(actor)s removed address '%(target)s'"),
    AuditEvent.ADDRESS_CREATED: _("%(actor)s added address '%(target)s'"),
    AuditEvent.ADDRESS_VERIFIED: _("%(actor)s succesfully validated address '%(target)s'"),

    AuditEvent.ASSIGNMENT_CREATED: _("%(actor)s assigned address to'%(target)s'"),
    AuditEvent.ASSIGNMENT_UPDATED: _("%(actor)s changed assignment for '%(target)s'"),
    AuditEvent.ASSIGNMENT_DELETED: _("%(actor)s removed assignment for '%(target)s'"),

    AuditEvent.SUBSCRIPTION_CREATED: _("%(actor)s subscribed to '%(target)s'"),
    AuditEvent.SUBSCRIPTION_DELETED: _("%(actor)s deleted subscription '%(target)s'"),
    AuditEvent.SUBSCRIPTION_ENABLED: _("%(actor)s enabled subscription '%(target)s'"),
    AuditEvent.SUBSCRIPTION_DISABLED: _("%(actor)s disabled subscription '%(target)s'"),

    AuditEvent.MEMBERSHIP_CREATED: _('%(actor)s add %(target)s to organization'),

    AuditEvent.CHANNEL_CREATED: _CREATED,
    AuditEvent.CHANNEL_DISABLED: _DISABLED,
    AuditEvent.CHANNEL_ENABLED: _ENABLED,
    AuditEvent.CHANNEL_UPDATED: _UPDATED,
    AuditEvent.CHANNEL_DELETED: _DELETED,
    AuditEvent.CHANNEL_DEPRECATED: _DEPRECATED,

    AuditEvent.MONITOR_CREATED: _CREATED,
    AuditEvent.MONITOR_DISABLED: _DISABLED,
    AuditEvent.MONITOR_ENABLED: _ENABLED,
    AuditEvent.MONITOR_UPDATED: _UPDATED,
    AuditEvent.MONITOR_DELETED: _DELETED,
    AuditEvent.MONITOR_TERMINATED: _('%(actor)s reach max number of allowed events'),

}


class AuditLogEntryyManager(models.Manager):
    def consolidate(self):
        for e in self.filter(organization__isnull=True):
            e.consolidate(async=False)


class AuditLogEntry(models.Model):
    AuditEvent = AuditEvent
    AUDITEVENT_CHOICES = [(tag.value, tag.name) for tag in AuditEvent]

    organization = models.ForeignKey('bitcaster.Organization',
                                     related_name='auditlog',
                                     on_delete=models.CASCADE)
    application = models.ForeignKey('bitcaster.Application',
                                    null=True, blank=True,
                                    related_name='auditlog',
                                    on_delete=models.CASCADE)
    actor = models.ForeignKey('bitcaster.User',
                              models.SET_NULL,
                              related_name='audit_actors', null=True, blank=True)
    actor_label = models.CharField(max_length=64, null=True, blank=True)

    target_label = models.CharField(max_length=300, null=True, blank=True)

    target_content_type = models.ForeignKey(ContentType,
                                            related_name='+',
                                            on_delete=models.SET_NULL,
                                            null=True, blank=True)
    target_object_id = models.PositiveIntegerField(null=True, blank=True)
    target = GenericForeignKey('target_content_type', 'target_object_id')

    event = models.IntegerField(choices=AUDITEVENT_CHOICES)

    ip_address = models.GenericIPAddressField(blank=True, null=True, unpack_ipv4=True)
    data = JSONField(blank=True, null=True)
    timestamp = models.DateTimeField(default=timezone.now)

    objects = AuditLogEntryyManager()

    def __str__(self):
        if self.event in MESSAGES:
            return MESSAGES[self.event] % dict(actor=self.actor.email,
                                               content_type=self.target_content_type,
                                               target=self.target_label,
                                               timestamp=self.timestamp, )
        else:
            return """Event #%(event)s %(actor)s - %(target)s """ % dict(
                event=self.event,
                actor=self.actor.email,
                content_type=self.target_content_type,
                target=self.target_label,
                timestamp=self.timestamp, )

    class Meta:
        get_latest_by = 'timestamp'
        ordering = ('timestamp',)
        app_label = 'bitcaster'

    @async(quque='consolidate')
    def consolidate(self):
        if hasattr(self.actor, 'application'):
            self.application = self.actor.application
        elif hasattr(self.actor, 'event'):
            self.application = self.actor.event.application

        if self.application:
            self.organization = self.application.organization

        self.actor_label = str(self.actor)
        self.target_label = str(self.target)
        self.save()

    @classmethod
    def log(self, event: int, actor: models.Model, **kwargs):
        AuditLogEntry.objects.create(event=event,
                                     actor=actor, **kwargs)

    def get_message(self):
        # msg = self.AuditEvent.get_by_value(self.event)
        return str(self)

    def get_actor_name(self):
        if self.actor:
            return self.actor.display_name
        return self.actor_label
