from django.contrib import admin

from bitcaster import models

from .address import AddressAdmin
from .api_key import ApiKeyAdmin
from .application import ApplicationAdmin
from .assignment import AssignmentAdmin
from .channel import ChannelAdmin
from .distribution import DistributionListAdmin
from .event import EventAdmin
from .group import GroupAdmin
from .internal import LogMessageAdmin
from .media import MediaFileAdmin
from .member import MemberAdmin
from .message import MessageTemplateAdmin
from .monitor import MonitorAdmin
from .notification import NotificationAdmin
from .occurrence import OccurrenceAdmin
from .organization import OrganizationAdmin
from .overrides import (
    FlagState,
    FlagStateAdmin,
    LogEntryAdmin,
)
from .project import ProjectAdmin
from .task import TaskAdmin
from .user import UserAdmin
from .user_message import UserMessageAdmin
from .userrole import UserRoleAdmin

admin.site.register(models.Group, GroupAdmin)
admin.site.register(models.LogEntry, LogEntryAdmin)

admin.site.unregister(FlagState)
admin.site.register(FlagState, FlagStateAdmin)


admin.site.register(models.Address, AddressAdmin)
admin.site.register(models.ApiKey, ApiKeyAdmin)
admin.site.register(models.Application, ApplicationAdmin)
admin.site.register(models.Assignment, AssignmentAdmin)
admin.site.register(models.Channel, ChannelAdmin)
admin.site.register(models.DistributionList, DistributionListAdmin)
admin.site.register(models.Event, EventAdmin)
admin.site.register(models.LogMessage, LogMessageAdmin)
admin.site.register(models.MediaFile, MediaFileAdmin)
admin.site.register(models.MessageTemplate, MessageTemplateAdmin)
admin.site.register(models.Member, MemberAdmin)
admin.site.register(models.Notification, NotificationAdmin)
admin.site.register(models.Occurrence, OccurrenceAdmin)
admin.site.register(models.Organization, OrganizationAdmin)
admin.site.register(models.Project, ProjectAdmin)
admin.site.register(models.User, UserAdmin)
admin.site.register(models.UserRole, UserRoleAdmin)
admin.site.register(models.UserMessage, UserMessageAdmin)
admin.site.register(models.Monitor, MonitorAdmin)
admin.site.register(models.Task, TaskAdmin)
