from django.contrib import admin
from django.contrib.auth.models import Group

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
from .media import MediaAdmin
from .message import MessageAdmin
from .monitor import MonitorAdmin
from .notification import NotificationAdmin
from .occurrence import OccurrenceAdmin
from .organization import OrganizationAdmin
from .overrides import (
    Config,
    ConstanceAdmin,
    FlagState,
    FlagStateAdmin,
    PeriodicTask,
    PeriodicTaskAdmin,
)
from .project import ProjectAdmin
from .user import UserAdmin
from .userrole import UserRoleAdmin

admin.site.unregister(Group)
admin.site.register(Group, GroupAdmin)

admin.site.unregister([Config])
admin.site.register([Config], ConstanceAdmin)

admin.site.unregister(FlagState)
admin.site.register(FlagState, FlagStateAdmin)

admin.site.unregister(PeriodicTask)
admin.site.register(PeriodicTask, PeriodicTaskAdmin)


admin.site.register(models.Address, AddressAdmin)
admin.site.register(models.ApiKey, ApiKeyAdmin)
admin.site.register(models.Application, ApplicationAdmin)
admin.site.register(models.Assignment, AssignmentAdmin)
admin.site.register(models.Channel, ChannelAdmin)
admin.site.register(models.DistributionList, DistributionListAdmin)
admin.site.register(models.Event, EventAdmin)
admin.site.register(models.LogMessage, LogMessageAdmin)
admin.site.register(models.MediaFile, MediaAdmin)
admin.site.register(models.Message, MessageAdmin)
admin.site.register(models.Notification, NotificationAdmin)
admin.site.register(models.Occurrence, OccurrenceAdmin)
admin.site.register(models.Organization, OrganizationAdmin)
admin.site.register(models.Project, ProjectAdmin)
admin.site.register(models.User, UserAdmin)
admin.site.register(models.UserRole, UserRoleAdmin)
admin.site.register(models.Monitor, MonitorAdmin)
