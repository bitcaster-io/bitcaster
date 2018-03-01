# -*- coding: utf-8 -*-
import logging

from django.contrib import admin

from mercury.models import Organization, OrganizationMember
from mercury.web.forms import OrganizationForm

from .inlines import ApplicationInline, OrganizationMemberInline
from .site import site

logger = logging.getLogger(__name__)


@admin.register(Organization, site=site)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'status', 'owner',)
    inlines = [ApplicationInline, OrganizationMemberInline]
    form = OrganizationForm


@admin.register(OrganizationMember, site=site)
class OrganizationMemberAdmin(admin.ModelAdmin):
    list_display = ('organization', 'user', 'role')
