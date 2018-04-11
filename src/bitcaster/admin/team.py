# -*- coding: utf-8 -*-
import logging

from django.contrib import admin

from bitcaster.admin.inlines import TeamMemberInline
from bitcaster.models import ApplicationTeam, Team

from .site import site

logger = logging.getLogger(__name__)


@admin.register(Team, site=site)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'status')
    inlines = [TeamMemberInline]


@admin.register(ApplicationTeam, site=site)
class ApplicationTeamAdmin(admin.ModelAdmin):
    list_display = ('application', 'team', 'role')
