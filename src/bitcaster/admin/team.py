# -*- coding: utf-8 -*-
import logging

from django.contrib import admin

from bitcaster.models import ApplicationTeam, Team

from .site import site

logger = logging.getLogger(__name__)


@admin.register(Team, site=site)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('organization', 'name', 'status')


@admin.register(ApplicationTeam, site=site)
class ApplicationTeamAdmin(admin.ModelAdmin):
    list_display = ('application', 'team', 'role')
