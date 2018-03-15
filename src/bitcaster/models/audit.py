# -*- coding: utf-8 -*-
"""
mercury / audit
~~~~~~~~~~~~~~~~~

:copyright: (c) 2018 Stefano Apostolico, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

import logging

from django.db import models
from django.utils.translation import gettext as _

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
    target_object = BoundedPositiveIntegerField(null=True)
    # TODO(dcramer): we want to compile this mapping into JSX for the UI
    event = BoundedPositiveIntegerField(
        choices=(
            # We emulate github a bit with event naming
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
            (AuditLogEntryEvent.PROJECT_SET_PUBLIC, 'project.set-public'),
            (AuditLogEntryEvent.PROJECT_SET_PRIVATE, 'project.set-private'),
            (AuditLogEntryEvent.PROJECT_REQUEST_TRANSFER, 'project.request-transfer'),
            (AuditLogEntryEvent.PROJECT_ACCEPT_TRANSFER, 'project.accept-transfer'),
            (AuditLogEntryEvent.ORG_ADD, 'org.create'),
            (AuditLogEntryEvent.ORG_EDIT, 'org.edit'),
            (AuditLogEntryEvent.ORG_REMOVE, 'org.remove'),
            (AuditLogEntryEvent.ORG_RESTORE, 'org.restore'),
            (AuditLogEntryEvent.TAGKEY_REMOVE, 'tagkey.remove'),
            (AuditLogEntryEvent.PROJECTKEY_ADD, 'projectkey.create'),
            (AuditLogEntryEvent.PROJECTKEY_EDIT, 'projectkey.edit'),
            (AuditLogEntryEvent.PROJECTKEY_REMOVE, 'projectkey.remove'),
            (AuditLogEntryEvent.PROJECTKEY_ENABLE, 'projectkey.enable'),
            (AuditLogEntryEvent.PROJECTKEY_DISABLE, 'projectkey.disable'),
            (AuditLogEntryEvent.SSO_ENABLE, 'sso.enable'),
            (AuditLogEntryEvent.SSO_DISABLE, 'sso.disable'),
            (AuditLogEntryEvent.SSO_EDIT, 'sso.edit'),
            (AuditLogEntryEvent.SSO_IDENTITY_LINK, 'sso-identity.link'),
            (AuditLogEntryEvent.APIKEY_ADD, 'api-key.create'),
            (AuditLogEntryEvent.APIKEY_EDIT, 'api-key.edit'),
            (AuditLogEntryEvent.APIKEY_REMOVE, 'api-key.remove'),
            (AuditLogEntryEvent.RULE_ADD, 'rule.create'),
            (AuditLogEntryEvent.RULE_EDIT, 'rule.edit'),
            (AuditLogEntryEvent.RULE_REMOVE, 'rule.remove'),
            (AuditLogEntryEvent.SET_ONDEMAND, 'ondemand.edit'),
            (AuditLogEntryEvent.SERVICEHOOK_ADD, 'serivcehook.create'),
            (AuditLogEntryEvent.SERVICEHOOK_EDIT, 'serivcehook.edit'),
            (AuditLogEntryEvent.SERVICEHOOK_REMOVE, 'serivcehook.remove'),
            (AuditLogEntryEvent.SERVICEHOOK_ENABLE, 'serivcehook.enable'),
            (AuditLogEntryEvent.SERVICEHOOK_DISABLE, 'serivcehook.disable'),
        )
    )
    ip_address = models.GenericIPAddressField(null=True, unpack_ipv4=True)
    data = GzippedDictField()
    datetime = models.DateTimeField(default=timezone.now)

    class Meta:
        app_label = 'sentry'
        db_table = 'sentry_auditlogentry'
