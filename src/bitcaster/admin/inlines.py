import logging

from django.contrib import admin

from bitcaster.models import (ApiAuthToken, Application, ApplicationTriggerKey,
                              Channel, Event, OrganizationMember,)
from bitcaster.models.message import Message
from bitcaster.utils.reflect import fqn

logger = logging.getLogger(__name__)


class ApiTokenInline(admin.TabularInline):
    model = ApiAuthToken
    extra = 0


class ApplicationTriggerKeyInline(admin.TabularInline):
    model = ApplicationTriggerKey
    extra = 0


class EventInline(admin.TabularInline):
    model = Event
    extra = 0
    show_change_link = True
    can_delete = False
    readonly_fields = fields = ('name',)


class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    show_change_link = True
    can_delete = False


class ChannelInline(admin.TabularInline):
    model = Channel
    extra = 0
    can_delete = False
    show_change_link = True
    readonly_fields = fields = ('name', 'dispatcher_name')

    def dispatcher_name(self, obj):
        return fqn(obj.handler)


class ApplicationInline(admin.TabularInline):
    model = Application
    extra = 0
    can_delete = False
    show_change_link = True
    readonly_fields = fields = ('name', 'timezone')


class OrganizationMemberInline(admin.TabularInline):
    model = OrganizationMember
    extra = 0
    can_delete = False
    show_change_link = True
    readonly_fields = fields = ('user', )

#
# class TeamMemberInline(admin.TabularInline):
#     model = TeamMembership
#     extra = 0
#     can_delete = False
#     show_change_link = True
