import logging

from django.contrib import admin

from bitcaster.models.invitation import Invitation

from .site import site

logger = logging.getLogger(__name__)


@admin.register(Invitation, site=site)
class InvitationAdmin(admin.ModelAdmin):
    list_display = ('target', 'organization', 'application', 'role', 'event')
    list_filter = ('organization', 'application', 'role', 'event')
    # form = OrganizationForm
