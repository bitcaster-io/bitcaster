import logging

from django.contrib import admin

from ..models import Address, AddressAssignment
from .site import site

logger = logging.getLogger(__name__)


@admin.register(Address, site=site)
class AddressAdmin(admin.ModelAdmin):
    search_fields = ('label', 'address')
    list_display = ('user', 'label', 'address', 'verified')
    list_filter = ('verified', )


@admin.register(AddressAssignment, site=site)
class AddressAssignmentAdmin(admin.ModelAdmin):
    search_fields = ('user__username',)
    list_display = ('user', 'address', 'channel')
    list_filter = ('channel',)
