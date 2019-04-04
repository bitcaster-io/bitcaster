import logging

from django.contrib import admin

from bitcaster.models import ApplicationTeam

from .site import site

logger = logging.getLogger(__name__)


@admin.register(ApplicationTeam, site=site)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('application', 'name', )
