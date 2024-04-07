from django.contrib import admin

from .. import models
from .auth import RoleAdmin, UserAdmin
from .org import ApplicationAdmin, OrganisationAdmin, ProjectAdmin
from .message import MessageAdmin
from .event import EventTypAdmin
from .channel import ChannelAdmin
from .subscription import SubscriptionAdmin


admin.site.register(models.Application, ApplicationAdmin)
admin.site.register(models.Channel, ChannelAdmin)
admin.site.register(models.EventType, EventTypAdmin)
admin.site.register(models.Message, MessageAdmin)
admin.site.register(models.Organization, OrganisationAdmin)
admin.site.register(models.Project, ProjectAdmin)
admin.site.register(models.Role, RoleAdmin)
admin.site.register(models.Subscription, SubscriptionAdmin)
admin.site.register(models.User, UserAdmin)
