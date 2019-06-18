import logging

from django.contrib import admin

from bitcaster.models.address import AddressAssignment

from ..models import Address
from .site import site

logger = logging.getLogger(__name__)


@admin.register(Address, site=site)
class AddressAdmin(admin.ModelAdmin):
    search_fields = ('label', 'address')
    list_display = ('user', 'label', 'address',)


@admin.register(AddressAssignment, site=site)
class AddressAssignmentAdmin(admin.ModelAdmin):
    search_fields = ('user__email', 'user__name',)
    list_display = ('user', 'address', 'channel', 'code', 'locked', 'verified')
    list_filter = ('verified', 'locked',)
    actions = ['verify']

    def verify(self, request, qs):
        qs.update(verified=True)
