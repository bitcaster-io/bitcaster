from constance.admin import Config

from django.contrib import admin

from bitcaster import models

from . import CustomConstanceAdmin
from .address import AddressAdmin
from .api_key import ApiKeyAdmin
from .application import ApplicationAdmin
from .assignment import AssignmentAdmin
from .attachment import AttachmentAdmin
from .channel import ChannelAdmin
from .client_token import ClientTokenAdmin
from .delivery import DeliveryAdmin
from .deliverysimulation import DeliverySimulationAdmin
from .distribution import DistributionListAdmin
from .event import EventAdmin
from .eventsimulation import EventSimulationAdmin
from .group import GroupAdmin
from .internal import LogMessageAdmin
from .media import MediaFileAdmin
from .member import MemberAdmin
from .membership import ApplicationMembershipAdmin
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
from .process_log import ProcessLogEntryAdmin
from .project import ProjectAdmin
from .subscription import SubscriptionAdmin
from .task import TaskAdmin
from .user import UserAdmin
from .user_message import UserMessageAdmin
from .userrole import UserRoleAdmin

admin.site.register(models.Group, GroupAdmin)
admin.site.register(models.LogEntry, LogEntryAdmin)

admin.site.unregister(FlagState)
admin.site.register(FlagState, FlagStateAdmin)

admin.site.unregister([Config])
admin.site.register([Config], CustomConstanceAdmin)

admin.site.register(models.Address, AddressAdmin)
admin.site.register(models.ApiKey, ApiKeyAdmin)
admin.site.register(models.Application, ApplicationAdmin)
admin.site.register(models.ApplicationMembership, ApplicationMembershipAdmin)
admin.site.register(models.Assignment, AssignmentAdmin)
admin.site.register(models.Attachment, AttachmentAdmin)
admin.site.register(models.Channel, ChannelAdmin)
admin.site.register(models.ClientToken, ClientTokenAdmin)
admin.site.register(models.DistributionList, DistributionListAdmin)
admin.site.register(models.Delivery, DeliveryAdmin)
admin.site.register(models.DeliverySimulation, DeliverySimulationAdmin)
admin.site.register(models.Event, EventAdmin)
admin.site.register(models.EventSimulation, EventSimulationAdmin)
admin.site.register(models.LogMessage, LogMessageAdmin)
admin.site.register(models.MediaFile, MediaFileAdmin)
admin.site.register(models.MessageTemplate, MessageTemplateAdmin)
admin.site.register(models.Member, MemberAdmin)
admin.site.register(models.Notification, NotificationAdmin)
admin.site.register(models.Occurrence, OccurrenceAdmin)
admin.site.register(models.Organization, OrganizationAdmin)
admin.site.register(models.ProcessLogEntry, ProcessLogEntryAdmin)
admin.site.register(models.Project, ProjectAdmin)
admin.site.register(models.Subscription, SubscriptionAdmin)
admin.site.register(models.User, UserAdmin)
admin.site.register(models.UserRole, UserRoleAdmin)
admin.site.register(models.UserMessage, UserMessageAdmin)
admin.site.register(models.Monitor, MonitorAdmin)
admin.site.register(models.Task, TaskAdmin)
