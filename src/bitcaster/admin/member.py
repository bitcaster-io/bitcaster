from typing import TYPE_CHECKING, Any, cast

import json

from admin_extra_buttons.decorators import button
from adminfilters.json_filter import JsonFieldFilter
from jsoneditor.forms import JSONEditor
from unfold.admin import TabularInline
from unfold.contrib.inlines.admin import NonrelatedTabularInline
from unfold.contrib.inlines.forms import NonrelatedInlineModelFormSet
from unfold.decorators import action

from django import forms
from django.contrib import messages
from django.contrib.admin import helpers
from django.db import transaction
from django.db.models import ForeignKey, Q, QuerySet, TextChoices
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from bitcaster.constants import Bitcaster, bitcaster
from bitcaster.forms import unfold as uwidgets
from bitcaster.forms.assignment import AssignmentInlineForm
from bitcaster.forms.user import GenericActionForm, SelectDistributionForm
from bitcaster.importing.members import import_members_csv
from bitcaster.models import Address, Assignment, DistributionList, Group, LogEntry, Member, Subscription, User
from bitcaster.utils.json import process_dict

from .base import BaseAdmin
from .filters import UserDistributionListFilter

if TYPE_CHECKING:  # pragma: no cover
    from django.forms import ModelChoiceField


class ReadOnlyInline:
    extra = 0
    tab = True

    def has_delete_permission(self, request: HttpRequest, obj: Any = None) -> bool:
        return False

    def has_add_permission(self, request: HttpRequest, obj: Any = None) -> bool:
        return False

    def has_change_permission(self, request: HttpRequest, obj: Any = None) -> bool:
        return False

    def save_new_instance(self, parent: Any, instance: Any) -> None:
        pass


class AddressInline(TabularInline):  # NonrelatedStackedInline is available as well
    model = Address
    fields = ["name", "value", "type"]  # Ignore property to display all fields
    extra = 0
    tab = True
    verbose_name = _("Address")
    verbose_name_plural = _("Addresses")
    collapsible = True

    def get_form_queryset(self, obj: Member) -> QuerySet[Address]:
        return Address.objects.filter(user=obj)

    def has_add_permission(self, request: HttpRequest, obj: Member | None = None) -> bool:
        return cast("bool", super().has_add_permission(request, obj) and obj and obj.pk)


class AssignmentFormSet(NonrelatedInlineModelFormSet):
    def get_form_kwargs(self, index: int) -> dict[str, Any]:
        ret = cast("dict[str, Any]", super().get_form_kwargs(index))
        ret["user"] = self.instance
        return ret


class AssignmentInline(NonrelatedTabularInline):  # NonrelatedStackedInline is available as well
    model = Assignment
    tab = True
    extra = 0
    form = AssignmentInlineForm
    autocomplete_fields = ["address"]
    formset = AssignmentFormSet

    def formfield_for_foreignkey(
        self, db_field: ForeignKey[Any], request: HttpRequest, **kwargs: Any
    ) -> "ModelChoiceField[Any] | None":
        ret = cast("ModelChoiceField[Any] | None", super().formfield_for_foreignkey(db_field, request, **kwargs))
        if db_field.name == "address" and ret:
            ret.queryset = Address.objects.none()
            if hasattr(ret.widget, "queryset"):
                ret.widget.queryset = Address.objects.none()
        return ret

    def get_form_queryset(self, obj: Member) -> QuerySet[Assignment]:
        return Assignment.objects.filter(address__user=obj)

    def save_new_instance(self, parent: Member, instance: Assignment) -> None:
        instance.save()

    def has_add_permission(self, request: HttpRequest, obj: Member | None = None) -> bool:
        return cast("bool", super().has_add_permission(request, obj) and obj and obj.pk)


class SubscriptionFormSet(NonrelatedInlineModelFormSet):
    def get_form_kwargs(self, index: int) -> dict[str, Any]:
        ret = cast("dict[str, Any]", super().get_form_kwargs(index))
        ret["user"] = self.instance
        return ret


class SubscriptionForm(forms.ModelForm["Subscription"]):
    assignment = forms.ModelChoiceField(
        label=_("Assignment"),
        queryset=Assignment.objects.none(),
        widget=uwidgets.UnfoldAdminSelectWidget,
    )

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if self.user is not None and self.user.pk:
            assignments = Assignment.objects.filter(address__user=self.user)
            self.fields["assignment"].queryset = assignments
            self.fields["assignment"].widget.queryset = assignments

    class Meta:
        model = Subscription
        fields = ("notification", "assignment", "active")


class SubscriptionInline(NonrelatedTabularInline):
    model = Subscription
    tab = True
    extra = 0
    form = SubscriptionForm
    formset = SubscriptionFormSet
    autocomplete_fields = ["notification"]
    readonly_fields = ["validity"]

    def get_formset(self, request: HttpRequest, obj: Member | None = None, **kwargs: Any) -> Any:
        self._request = request
        return super().get_formset(request, obj, **kwargs)

    def get_form_queryset(self, obj: Member) -> QuerySet[Subscription]:
        return Subscription.objects.filter(assignment__address__user=obj).select_related(
            "notification__event", "assignment__channel"
        )

    def save_new_instance(self, parent: Member, instance: Subscription) -> None:
        instance.full_clean()
        instance.save()
        if not instance.is_valid:
            messages.warning(
                self._request,
                _(
                    "Subscription created but cannot be used: the assignment channel is not enabled "
                    "for the notification event."
                ),
            )

    def has_add_permission(self, request: HttpRequest, obj: Member | None = None) -> bool:
        return cast("bool", super().has_add_permission(request, obj) and obj and obj.pk)


class ListsForm(forms.ModelForm):
    dl = forms.ModelChoiceField(
        label=_("Distribution List"),
        queryset=DistributionList.objects.all(),
        required=True,
        widget=uwidgets.UnfoldAdminSelectWidget,
    )
    assignment = forms.ModelChoiceField(
        label=_("Assignment"),
        queryset=Assignment.objects.none(),
        required=True,
        widget=uwidgets.UnfoldAdminSelectWidget,
    )

    class Meta:
        model = DistributionList
        fields = ["dl", "assignment"]

    def __init__(
        self,
        *args: Any,
        user: Member | None = None,
        dl_initial: DistributionList | None = None,
        assignment_initial: Assignment | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.user = user
        user_id = user.pk if user else None
        self.fields["assignment"].queryset = Assignment.objects.filter(address__user_id=user_id)
        if dl_initial is not None:
            self.fields["dl"].initial = dl_initial
            self.fields["dl"].disabled = True
            if assignment_initial is not None:
                self.fields["assignment"].initial = assignment_initial
                self.fields["assignment"].disabled = True
        else:
            self.fields["dl"].queryset = DistributionList.objects.exclude(
                recipients__address__user_id=user_id
            ).distinct()


class ListsFormSet(NonrelatedInlineModelFormSet):
    def get_form_kwargs(self, index: int | None) -> dict[str, Any]:
        ret = cast("dict[str, Any]", super().get_form_kwargs(index))
        ret["user"] = self.instance
        if index is not None and index < self.initial_form_count():
            dl = self.queryset.all()[index]
            ret["dl_initial"] = dl
            ret["assignment_initial"] = dl.recipients.filter(
                address__user_id=self.instance.pk if self.instance else None
            ).first()
        return ret

    def save_new(self, form: forms.ModelForm, commit: bool = True) -> DistributionList:
        dl = form.cleaned_data["dl"]
        asm = form.cleaned_data["assignment"]
        if dl is not None and asm is not None:
            dl.recipients.add(asm)
        return cast("DistributionList", dl)


class ListsInline(NonrelatedTabularInline):  # NonrelatedStackedInline is available as well
    model = DistributionList
    tab = True
    fields = ["dl", "assignment"]
    extra = 1
    form = ListsForm
    formset = ListsFormSet

    def get_readonly_fields(self, request: HttpRequest, obj: Member | None = None) -> list[str]:
        return []

    def get_form_queryset(self, obj: Member) -> QuerySet[DistributionList]:
        return obj.get_distribution_lists()

    def save_new_instance(self, parent: Member, instance: DistributionList) -> None:
        instance.save()


class JsonUpdateMode2(TextChoices):
    # we do not support all bitcaster.utils.json.JsonUpdateMode options
    MERGE = "merge", "merge"
    REMOVE = "remove", "remove"
    REWRITE = "rewrite", "rewrite"
    OVERRIDE = "override", "override"


def check_custom_fields(v: Any) -> Any:
    try:
        if isinstance(v, str):
            v = json.loads(v)
        if not isinstance(v, dict):
            raise forms.ValidationError(_("Must be a dictionary."))
    except json.JSONDecodeError:
        raise forms.ValidationError(_("Invalid JSON.")) from None
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

    def clean_custom_fields(self) -> Any:
        return check_custom_fields(self.cleaned_data["custom_fields"])


class MemberForm(forms.ModelForm[Member]):
    custom_fields = forms.CharField(widget=JSONEditor(jsonschema=CustomFieldForm.schema))

    class Meta:
        model = Member
        fields = ["username", "first_name", "last_name", "email", "custom_fields"]

    def clean_custom_fields(self) -> Any:
        return check_custom_fields(self.cleaned_data["custom_fields"])


class ImportForm(forms.Form):
    file = forms.FileField(widget=uwidgets.UnfoldAdminFileFieldWidget)
    group = forms.ModelChoiceField(queryset=Group.objects.all(), required=True, widget=uwidgets.UnfoldAdminSelectWidget)


class MemberAdmin(BaseAdmin[Member]):
    list_display = ("username", "first_name", "last_name", "email")
    list_filter = (
        ("custom_fields", JsonFieldFilter.factory(options=False)),
        UserDistributionListFilter,
    )
    inlines = [AddressInline, AssignmentInline, SubscriptionInline, ListsInline]

    def changelist_view(self, request: HttpRequest, extra_context: dict[str, Any] | None = None) -> TemplateResponse:
        extra_context = extra_context or {}
        dl_id = request.GET.get("dl")
        if dl_id:
            try:
                dl = DistributionList.objects.get(pk=dl_id)
                extra_context["subtitle"] = _("Members selected for distribution list: %s") % dl.name
            except (DistributionList.DoesNotExist, ValueError):
                pass
        return super().changelist_view(request, extra_context=extra_context)

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

    def get_readonly_fields(self, request: HttpRequest, obj: User | None = None) -> list[str]:
        return ["username", "email", "last_login", "date_joined"]

    def add_to_distributionlist(self, request: HttpRequest, queryset: QuerySet[User]) -> HttpResponse:
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
                self.message_user(request, str(_("Users successfully added")))
                return HttpResponseRedirect(reverse(f"{self.admin_site.name}:bitcaster_user_changelist"))
        else:
            form = SelectDistributionForm(initial=initial)
        ctx["form"] = form
        return TemplateResponse(request, "bitcaster/admin/user/add_to_distributionlist.html", ctx)

    @button(label="Import Members")  # type: ignore[arg-type]
    def import_members(self, request: HttpRequest) -> HttpResponse:
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

    @action(description="Update Custom fields", icon="person")  # type: ignore[untyped-decorator]
    def update_custom_fields(self, request: HttpRequest, queryset: QuerySet[Member]) -> HttpResponse:
        ctx = self.get_common_context(request, action_title="Update Custom Fields")
        if request.method == "POST" and "apply" in request.POST:
            form = CustomFieldForm(request.POST)
            if form.is_valid():
                with transaction.atomic():
                    if form.cleaned_data["mode"] == JsonUpdateMode2.REWRITE:
                        queryset.update(custom_fields=form.cleaned_data["custom_fields"])
                    else:
                        for __, record in enumerate(queryset):
                            updated = process_dict(
                                record.custom_fields, form.cleaned_data["custom_fields"], form.cleaned_data["mode"]
                            )
                            record.custom_fields = updated
                            record.save()
                LogEntry.objects.log_actions(
                    user_id=str(request.user.pk),
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

    def get_queryset(self, request: HttpRequest) -> QuerySet[Member]:
        return cast("QuerySet[Member]", Member.objects.exclude(Q(username=Bitcaster.SYSTEM_USER)).order_by("username"))
