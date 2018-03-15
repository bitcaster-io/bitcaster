# -*- coding: utf-8 -*-
import logging

from django.db import models

from bitcaster.models import Organization, Application

logger = logging.getLogger(__name__)


class AuditLogEntryEvent(object):
    MEMBER_INVITE = 1
    MEMBER_ADD = 2
    MEMBER_ACCEPT = 3
    MEMBER_EDIT = 4
    MEMBER_REMOVE = 5
    MEMBER_JOIN_TEAM = 6
    MEMBER_LEAVE_TEAM = 7

    ORG_ADD = 10
    ORG_EDIT = 11
    ORG_REMOVE = 12
    ORG_RESTORE = 13

    TEAM_ADD = 20
    TEAM_EDIT = 21
    TEAM_REMOVE = 22

    PROJECT_ADD = 30
    PROJECT_EDIT = 31
    PROJECT_REMOVE = 32


class AuditLog(models.Model):
    organization = models.ForeignKey(Organization,
                                     on_delete=models.CASCADE)
    application = models.ForeignKey(Application,
                                    on_delete=models.CASCADE)
    actor_label = models.CharField(max_length=64, null=True, blank=True)
    event = models.PositiveIntegerField(
        choices=(
            (AuditLogEntryEvent.MEMBER_INVITE, 'member.invite'),
            (AuditLogEntryEvent.MEMBER_ADD, 'member.add'),
            (AuditLogEntryEvent.MEMBER_ACCEPT, 'member.accept-invite'),
            (AuditLogEntryEvent.MEMBER_REMOVE, 'member.remove'),
            (AuditLogEntryEvent.MEMBER_EDIT, 'member.edit'),
            (AuditLogEntryEvent.MEMBER_JOIN_TEAM, 'member.join-team'),
            (AuditLogEntryEvent.MEMBER_LEAVE_TEAM, 'member.leave-team'),
            (AuditLogEntryEvent.TEAM_ADD, 'team.create'),
            (AuditLogEntryEvent.TEAM_EDIT, 'team.edit'),
            (AuditLogEntryEvent.TEAM_REMOVE, 'team.remove'),
            (AuditLogEntryEvent.PROJECT_ADD, 'project.create'),
            (AuditLogEntryEvent.PROJECT_EDIT, 'project.edit'),
            (AuditLogEntryEvent.PROJECT_REMOVE, 'project.remove'),
            (AuditLogEntryEvent.ORG_ADD, 'org.create'),
            (AuditLogEntryEvent.ORG_EDIT, 'org.edit'),
            (AuditLogEntryEvent.ORG_REMOVE, 'org.remove'),
            (AuditLogEntryEvent.ORG_RESTORE, 'org.restore'),
        )
    )
    ip_address = models.GenericIPAddressField(null=True, unpack_ipv4=True)
    data = JsonField()
    datetime = models.DateTimeField(default=timezone.now)
