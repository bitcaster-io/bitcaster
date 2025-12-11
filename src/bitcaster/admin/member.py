from adminfilters.json_filter import JsonFieldFilter
from django.db.models import Q
from unfold.admin import TabularInline
from unfold.contrib.inlines.admin import NonrelatedTabularInline

from bitcaster.admin.base import BaseAdmin, BitcasterModelAdmin
from bitcaster.constants import Bitcaster
from bitcaster.models import Address, Assignment, DistributionList, Member


class ReadOnlyInline:
    extra = 0
    tab = True

    def has_delete_permission(self, request, obj):
        return False

    def has_add_permission(self, request, obj):
        return False

    def has_change_permission(self, request, obj):
        return False


class AddressInline(TabularInline):  # NonrelatedStackedInline is available as well
    model = Address
    fields = ["name", "type"]  # Ignore property to display all fields
    extra = 0


class AssignmentInline(ReadOnlyInline, NonrelatedTabularInline):  # NonrelatedStackedInline is available as well
    model = Assignment
    fields = ["channel", "address", "validated", "active"]  # Ignore property to display all fields
    readonly_fields = ["address", "channel"]

    def get_form_queryset(self, obj: Member):
        return Assignment.objects.filter(address__user=obj)

    def save_new_instance(self, parent, instance):
        pass


class ListsInline(ReadOnlyInline, NonrelatedTabularInline):  # NonrelatedStackedInline is available as well
    model = DistributionList
    fields = ["name", "project"]  # Ignore property to display all fields
    readonly_fields = ["name", "project"]

    def get_form_queryset(self, obj: Member):
        return obj.distribution_lists

    def save_new_instance(self, parent, instance):
        pass


class MemberAdmin(BaseAdmin, BitcasterModelAdmin[Member]):
    list_display = ("username", "first_name", "last_name", "email")
    fields = ("username", "first_name", "last_name", "email", "custom_fields")
    list_filter = (("custom_fields", JsonFieldFilter.factory()),)
    inlines = [AddressInline, AssignmentInline, ListsInline]

    def get_queryset(self, request):
        return Member.objects.exclude(Q(username=Bitcaster.SYSTEM_USER) | Q(is_staff=True, is_superuser=True)).order_by(
            "username"
        )
