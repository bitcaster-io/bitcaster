from enum import IntEnum

from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext as _


class AuditEvent(IntEnum):
    MEMBER_LOGIN = 0
    MEMBER_LOGOUT = 1

    # Invitations 2xx
    INVITATION_CREATED = 201
    INVITATION_SENT = 202
    INVITATION_ACCEPTED = 203

    # user
    MEMBER_UPDATE_PROFILE = 301
    MEMBER_UPDATE_ADDRESS = 302
    MEMBER_DELETE_ADDRESS = 303
    MEMBER_ADD_ADDRESS = 304
    MEMBER_VALIDATE_ADDRESS = 305

    MEMBER_ADD_ASSIGNMENT = 401
    MEMBER_CHANGE_ASSIGNMENT = 402
    MEMBER_DELETE_ASSIGNMENT = 403

    MEMBER_SUBSCRIBE_EVENT = 505
    MEMBER_DELETE_SUBSCRIPTION = 506
    MEMBER_ENABLE_SUBSCRIPTION = 507
    MEMBER_DISABLE_SUBSCRIPTION = 507

    MEMBERSHIP_CREATED = 601

    # SUBSCRIPTION_ERROR = 701
    #
    # @classmethod
    # def get_by_value(cls, v):
    #     try:
    #         label = ([val for val in cls if val == v][0]).name
    #         return label.replace('_', ' ').title()
    #     except IndexError:
    #         return 'N/A (%s)' % v


MESSAGES = {
    AuditEvent.MEMBER_LOGIN: _('%(actor)s logged in'),
    AuditEvent.MEMBER_LOGOUT: _('%(actor)s logged out'),

    AuditEvent.INVITATION_CREATED: _("%(actor)s invited '%(target)s'"),
    AuditEvent.INVITATION_SENT: _("%(actor)s sent invitation to '%(target)s'"),
    AuditEvent.INVITATION_ACCEPTED: _('%(actor)s accepted invitation'),

    AuditEvent.MEMBER_UPDATE_PROFILE: _('%(actor)s updated profile'),
    AuditEvent.MEMBER_UPDATE_ADDRESS: _("%(actor)s updated address '%(target)s'"),
    AuditEvent.MEMBER_DELETE_ADDRESS: _("%(actor)s removed address '%(target)s'"),
    AuditEvent.MEMBER_ADD_ADDRESS: _("%(actor)s added address '%(target)s'"),
    AuditEvent.MEMBER_VALIDATE_ADDRESS: _("%(actor)s succesfully validated address '%(target)s'"),

    AuditEvent.MEMBER_ADD_ASSIGNMENT: _("%(actor)s assigned address to'%(target)s'"),
    AuditEvent.MEMBER_CHANGE_ASSIGNMENT: _("%(actor)s changed assignment for '%(target)s'"),
    AuditEvent.MEMBER_DELETE_ASSIGNMENT: _("%(actor)s removed assignment for '%(target)s'"),

    AuditEvent.MEMBER_DELETE_SUBSCRIPTION: _("%(actor)s deleted subscription '%(target)s'"),
    AuditEvent.MEMBER_ENABLE_SUBSCRIPTION: _("%(actor)s enabled subscription '%(target)s'"),
    AuditEvent.MEMBER_DISABLE_SUBSCRIPTION: _("%(actor)s disabled subscription '%(target)s'"),
    AuditEvent.MEMBER_SUBSCRIBE_EVENT: _("%(actor)s subscribed to '%(target)s'"),

    AuditEvent.MEMBERSHIP_CREATED: _('%(actor)s add %(target)s to organization'),

}


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
    actor = models.ForeignKey('bitcaster.User', models.SET_NULL,
                              related_name='audit_actors', null=True, blank=True)
    actor_label = models.CharField(max_length=64, null=True, blank=True)

    target_object = models.PositiveIntegerField(blank=True, null=True)
    target_label = models.CharField(max_length=300, null=True, blank=True)

    event = models.IntegerField(choices=AUDITEVENT_CHOICES)

    ip_address = models.GenericIPAddressField(blank=True, null=True, unpack_ipv4=True)
    data = JSONField(blank=True, null=True)
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return MESSAGES.get(self.event, '') % dict(actor=self.actor,
                                                   target=self.target_label,
                                                   timestamp=self.timestamp, )

    class Meta:
        get_latest_by = 'timestamp'
        ordering = ('timestamp',)
        app_label = 'bitcaster'

    def get_message(self):
        # msg = self.AuditEvent.get_by_value(self.event)
        return str(self)

    def save(self, *args, **kwargs):
        if not self.actor_label:
            if self.actor:
                self.actor_label = self.actor.display_name
        super(AuditLogEntry, self).save(*args, **kwargs)

    def get_actor_name(self):
        if self.actor:
            return self.actor.display_name
        return self.actor_label
