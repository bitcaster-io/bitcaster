import logging

from django.contrib import admin

from bitcaster.models import Application, ApplicationUser

from .forms import ApplicationForm
from .inlines import ChannelInline, EventInline
from .site import site

logger = logging.getLogger(__name__)


@admin.register(Application, site=site)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('organization', 'name', 'timezone', )
    list_filter = ('organization', )
    inlines = [ChannelInline, EventInline]
    form = ApplicationForm


@admin.register(ApplicationUser, site=site)
class ApplicationMemberAdmin(admin.ModelAdmin):
    list_display = ('application', 'user', 'role',)
