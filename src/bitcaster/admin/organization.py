# -*- coding: utf-8 -*-
import logging

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django_extensions.admin.filter import NullFieldListFilter

from bitcaster.models import Organization, OrganizationMember

from .inlines import ApplicationInline, OrganizationMemberInline
from .site import site

logger = logging.getLogger(__name__)


@admin.register(Organization, site=site)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'status', 'owner',)
    inlines = [ApplicationInline, OrganizationMemberInline]
    # form = OrganizationForm


class StatusFilter(NullFieldListFilter):
    def lookups(self, request, model_admin):
        return (
            ('1', _('Pending')),
            ('0', _('Concluded')),
        )


@admin.register(OrganizationMember, site=site)
class OrganizationMemberAdmin(admin.ModelAdmin):
    list_display = ('organization', 'll', 'date_added',
                    'role', 'date_enrolled', )
    list_filter = ('organization', 'role', ('user', StatusFilter))

    def ll(self, obj):
        if obj.user:
            return obj.user.email
        return obj.email
    ll.verbose_name = 'aaaa'
    ll.label = 'aaaa'
