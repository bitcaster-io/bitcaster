from django.contrib import admin

from bitcaster import models

from .address import AddressAdmin, ValidationAdmin
from .auth import RoleAdmin, UserAdmin
from .channel import ChannelAdmin
from .event import EventAdmin
from .log import LogMessageAdmin
from .message import MessageAdmin
from .org import ApplicationAdmin, OrganisationAdmin, ProjectAdmin
from .subscription import SubscriptionAdmin

admin.site.register(models.Address, AddressAdmin)
admin.site.register(models.Application, ApplicationAdmin)
admin.site.register(models.Channel, ChannelAdmin)
admin.site.register(models.Event, EventAdmin)
admin.site.register(models.LogMessage, LogMessageAdmin)
admin.site.register(models.Message, MessageAdmin)
admin.site.register(models.Organization, OrganisationAdmin)
admin.site.register(models.Project, ProjectAdmin)
admin.site.register(models.Role, RoleAdmin)
admin.site.register(models.Subscription, SubscriptionAdmin)
admin.site.register(models.User, UserAdmin)
admin.site.register(models.Validation, ValidationAdmin)
