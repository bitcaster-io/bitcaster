import json
from typing import TYPE_CHECKING

from admin_extra_buttons.decorators import button
from adminfilters.json_filter import JsonFieldFilter
from django import forms
from django.contrib import messages
from django.contrib.admin import helpers
from django.db import transaction
from django.db.models import Q, QuerySet, TextChoices
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from jsoneditor.forms import JSONEditor
from unfold.admin import TabularInline
from unfold.contrib.inlines.admin import NonrelatedTabularInline
from unfold.decorators import action

from bitcaster.constants import Bitcaster, bitcaster
from bitcaster.forms import unfold as uwidgets
from bitcaster.forms.user import GenericActionForm, SelectDistributionForm
from bitcaster.models import Address, Assignment, DistributionList, Group, LogEntry, Member, User
from bitcaster.utils.json import process_dict

from ..importing.members import import_members_csv
from .base import BaseAdmin, BitcasterModelAdmin

if TYPE_CHECKING:
    from django.http import HttpRequest, HttpResponse

    from bitcaster.types.json import JSON


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


class JsonUpdateMode2(TextChoices):
    # we do not support all bitcaster.utils.json.JsonUpdateMode options
    MERGE = "merge"
    REMOVE = "remove"
    REWRITE = "rewrite"
    OVERRIDE = "override"


def check_custom_fields(v: "JSON") -> "JSON":
    try:
        v = json.loads(v)
        if not isinstance(v, dict):
            raise forms.ValidationError("Must be a dictionary.")
    except json.JSONDecodeError:
        raise forms.ValidationError("Invalid JSON.") from None
    return v


class CustomFieldForm(GenericActionForm):
    schema = {
        "type": "object",
        "additionalProperties": {"$ref": "#/$defs/jsonValue"},
        "$defs": {
            "jsonValue": {
                "oneOf": [
                    {"$ref": "#/$defs/jsonScalar"},
                    {"type": "array", "items": {"$ref": "#/$defs/jsonValue"}},
                    {"type": "object", "additionalProperties": {"$ref": "#/$defs/jsonValue"}},
                ]
            },
            "jsonScalar": {"oneOf": [{"type": "string"}, {"type": "number"}, {"type": "boolean"}, {"type": "null"}]},
        },
    }
    mode = forms.ChoiceField(choices=JsonUpdateMode2.choices, widget=uwidgets.UnfoldAdminSelectWidget)
    custom_fields = forms.CharField(widget=JSONEditor(jsonschema=schema), required=False)

    def clean_custom_fields(self):
        return check_custom_fields(self.cleaned_data["custom_fields"])


class MemberForm(forms.ModelForm):
    custom_fields = forms.CharField(widget=JSONEditor(jsonschema=CustomFieldForm.schema))

    class Meta:
        model = Member
        fields = ["username", "first_name", "last_name", "email", "custom_fields"]

    def clean_custom_fields(self):
        return check_custom_fields(self.cleaned_data["custom_fields"])


class ImportForm(forms.Form):
    file = forms.FileField(widget=uwidgets.UnfoldAdminFileFieldWidget)
    group = forms.ModelChoiceField(queryset=Group.objects.all(), required=True, widget=uwidgets.UnfoldAdminSelectWidget)


class MemberAdmin(BaseAdmin, BitcasterModelAdmin[Member]):
    list_display = ("username", "first_name", "last_name", "email")
    list_filter = (("custom_fields", JsonFieldFilter.factory()),)
    inlines = [AddressInline, AssignmentInline, ListsInline]
    actions = ["update_custom_fields", "add_to_distributionlist"]
    search_fields = ("username", "first_name", "last_name", "email")
    form = MemberForm
    fieldsets = (
        (_("Personal info"), {"classes": ["tab"], "fields": ("first_name", "last_name", "email")}),
        (_("Account"), {"classes": ["tab"], "fields": ("username",)}),
        (_("Important dates"), {"classes": ["tab"], "fields": ("last_login", "date_joined")}),
        (_("Options"), {"classes": ["tab"], "fields": ("timezone", "date_time_format", "date_format")}),
        (_("Extended"), {"classes": ["tab"], "fields": ("custom_fields",)}),
    )

    def get_readonly_fields(self, request: "HttpRequest", obj: "User|None" = None) -> list[str]:
        return ["username", "email", "last_login", "date_joined"]

    def add_to_distributionlist(self, request: "HttpRequest", queryset: "QuerySet[User]") -> "HttpResponse":
        ctx = self.get_common_context(request, title=_("Add to Distribution List"))
        initial = {
            "_selected_action": request.POST.getlist(helpers.ACTION_CHECKBOX_NAME),
            "select_across": request.POST.get("select_across") == "1",
            "action": request.POST.get("action", ""),
        }
        if "apply" in request.POST:
            form = SelectDistributionForm(request.POST, request.FILES)
            if form.is_valid():
                dl: DistributionList = form.cleaned_data["dl"]
                for user in queryset:
                    if asm := Assignment.objects.filter(address__user=user).first():
                        dl.recipients.add(asm)
                self.message_user(request, _("Users successfully added"))
                return HttpResponseRedirect(reverse(f"{self.admin_site.name}:bitcaster_user_changelist"))
        else:
            form = SelectDistributionForm(initial=initial)
        ctx["form"] = form
        return TemplateResponse(request, "bitcaster/admin/user/add_to_distributionlist.html", ctx)

    @button(label="Import Members")
    def import_members(self, request) -> "HttpResponse":
        ctx = self.get_common_context(request, action_title="Import Members")
        if "apply" in request.POST:
            form = ImportForm(request.POST, request.FILES, initial={"group": bitcaster.get_default_group()})
            if form.is_valid():
                f = form.cleaned_data.pop("file")
                imported, processed = import_members_csv(f, group=form.cleaned_data["group"])
                self.message_user(request, f"Record successfully imported {imported}/{processed}", messages.SUCCESS)
                return HttpResponseRedirect("..")
        else:
            form = ImportForm(initial={"group": bitcaster.get_default_group()})
        ctx["form"] = form
        return render(request, "bitcaster/admin/members/import_members.html", ctx)

    @action(description="Update Custom fields", icon="person")
    def update_custom_fields(self, request: "HttpRequest", queryset: "QuerySet") -> "HttpResponse":
        ctx = self.get_common_context(request, action_title="Update Custom Fields")
        if request.method == "POST" and "apply" in request.POST:
            form = CustomFieldForm(request.POST)
            if form.is_valid():
                with transaction.atomic():
                    if form.cleaned_data["mode"] == JsonUpdateMode2.REWRITE:
                        queryset.update(custom_fields=form.cleaned_data["custom_fields"])
                    else:
                        for __, record in enumerate(queryset.only("pk", "custom_fields")):
                            updated = process_dict(
                                record.custom_fields, form.cleaned_data["custom_fields"], form.cleaned_data["mode"]
                            )
                            record.custom_fields = updated
                            record.save()
                LogEntry.objects.log_actions(
                    user_id=self.request.user.pk,
                    queryset=queryset,
                    action_flag=LogEntry.OTHER,
                    change_message="Custom field mass-updated",
                )
                self.message_user(request, "Record successfully updated", messages.SUCCESS)
                return HttpResponseRedirect(".")
        else:
            form = CustomFieldForm(
                initial={
                    "custom_fields": {},
                    "action": request.POST.get("action"),
                    "_selected_action": request.POST.getlist("_selected_action"),
                    "select_across": request.POST.get("select_across"),
                }
            )

        ctx["form"] = form
        return render(request, "bitcaster/admin/user/update_custom_fields.html", ctx)

    def get_queryset(self, request):
        return Member.objects.exclude(Q(username=Bitcaster.SYSTEM_USER)).order_by("username")
