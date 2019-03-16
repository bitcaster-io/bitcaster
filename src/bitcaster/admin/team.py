# -*- coding: utf-8 -*-
import logging

from django.contrib import admin

from bitcaster.models import ApplicationRole, Team

from .site import site

logger = logging.getLogger(__name__)


@admin.register(Team, site=site)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('application', 'name', 'status')


@admin.register(ApplicationRole, site=site)
class ApplicationTeamAdmin(admin.ModelAdmin):
    list_display = ('team', 'role')
