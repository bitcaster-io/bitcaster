import logging
from typing import TYPE_CHECKING, Any

from admin_extra_buttons.buttons import ButtonWidget
from admin_extra_buttons.decorators import button, link
from adminfilters.autocomplete import LinkedAutoCompleteFilter
from constance import config
from django import forms
from django.contrib.admin.helpers import AdminForm
from django.core.exceptions import PermissionDenied
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.translation import gettext as _
from formtools.wizard.views import CookieWizardView
from reversion.admin import VersionAdmin

from bitcaster.models import Assignment, Channel, Organization, Project, User

from ..dispatchers.base import Payload, dispatcherManager
from ..forms.channel import ChannelChangeForm
from .base import BaseAdmin, ButtonColor
from .filters import ChannelTypeFilter
from .mixins import LockMixinAdmin, TwoStepCreateMixin

if TYPE_CHECKING:
    from django.utils.datastructures import _ListOrTuple
    from formtools.wizard.storage.session import SessionStorage

    from bitcaster.types.django import AnyModel
    from bitcaster.types.http import AuthHttpRequest

logger = logging.getLogger(__name__)


class ChannelTestForm(forms.Form):
    subject = forms.CharField(required=False)
    message = forms.CharField(widget=forms.Textarea)


class WizardForm(forms.Form):
    def __init__(self, request: HttpRequest, **kwargs: Any) -> None:
        self.request = request
        super().__init__(**kwargs)


class SelectOrganizationForm(WizardForm):
    help_text = _(
        """
Select the organization that this channel belongs to.
    """
    )
    organization = forms.ModelChoiceField(queryset=Organization.objects.all())

    @staticmethod
    def visible(w: "ChannelWizard") -> bool:
        return not (w.request and ("organization" in w.request.GET or "project" in w.request.GET))


class ChannelProject(WizardForm):
    help_text = _(
        """
Choose the specific project that this channel belongs to.
    """
    )
    project = forms.ModelChoiceField(required=True, queryset=Project.objects.all())

    @staticmethod
    def visible(w: "ChannelWizard") -> bool:
        if w.request and "project" in w.request.GET:
            return False
        return w.get_selected_mode() in ["inherit", "new"]


class ChannelType(WizardForm):
    MODE_NEW = "new"
    MODE_INHERIT = "inherit"
    MODE_TEMPLATE = "template"
    MODE_CHOICES = (
        (MODE_NEW, _("Create New Project Channel")),
        (MODE_INHERIT, _("Enable Abstract Channel")),
        (MODE_TEMPLATE, _("Create Abstract Channel")),
    )
    help_text = _(
        """
Select the type of channel you want to create. see [[doc:help/channel:Channel]]
    """
    )
    operation = forms.ChoiceField(
        choices=MODE_CHOICES,
        widget=forms.RadioSelect,
    )

    def __init__(self, request: HttpRequest, **kwargs: Any) -> None:
        super().__init__(request, **kwargs)
        if "project" in request.GET:
            self.fields["operation"].choices = [
                c for c in self.fields["operation"].choices if c[0] != ChannelType.MODE_TEMPLATE
            ]
        elif "organization" in request.GET:
            self.fields["operation"].choices = [
                c for c in self.fields["operation"].choices if c[0] == ChannelType.MODE_TEMPLATE
            ]

    @staticmethod
    def visible(w: "ChannelWizard") -> bool:
        return not (w.request and "organization" in w.request.GET)


class ChannelSelectParent(WizardForm, forms.ModelForm[Channel]):
    help_text = _(
        """
Select the abstract channel that you want to make available for this project.
    """
    )
    parent = forms.ModelChoiceField(label=_("Abstract"), queryset=Channel.objects.all(), required=True)

    class Meta:
        model = Channel
        fields = (
            "parent",
            "name",
            # "project",
        )

    @staticmethod
    def visible(w: "ChannelWizard") -> bool:
        return w.get_selected_mode() == ChannelType.MODE_INHERIT


class ChannelData(WizardForm, forms.ModelForm[Channel]):
    help_text = _(
        """
Provide a name for this channel and the Dispatcher to use. You will be asked for specific information after this step.
    """
    )

    class Meta:
        model = Channel
        fields = ("name", "dispatcher")

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.fields["dispatcher"].choices = dispatcherManager.as_choices()

    @staticmethod
    def visible(w: "ChannelWizard") -> bool:
        return w.get_selected_mode() in [ChannelType.MODE_TEMPLATE, ChannelType.MODE_NEW]


class ManagementForm(forms.Form):
    prefix = "mng"
    current_step = forms.IntegerField()


class ChannelWizard(CookieWizardView):
    form_list = (
        ("mode", ChannelType),
        ("org", SelectOrganizationForm),
        ("prj", ChannelProject),
        ("parent", ChannelSelectParent),
        ("data", ChannelData),
    )
    condition_dict = {
        # "mode": ChannelType.visible,
        "org": SelectOrganizationForm.visible,
        "prj": ChannelProject.visible,
        "parent": ChannelSelectParent.visible,
        "data": ChannelData.visible,
    }
    template_name = "admin/channel/add_view.html"

    def get_selected_mode(self) -> str | None:
        if "mode" in self.storage.data.get("step_data"):
            return self.storage.get_step_data("mode")["mode-operation"]
        return None

    def get_form_kwargs(self, step: str | None = None) -> dict[str, Any]:
        ret = super().get_form_kwargs(step)
        ret["request"] = self.request
        return ret

    def get_form(self, step: str | None = None, data: Any = None, files: Any = None) -> forms.Form:
        form = super().get_form(step, data, files)
        if step == "org":
            form.fields["organization"].queryset = Organization.objects.local()
        elif step == "prj":
            selected_org = self.storage.get_step_data("org").get("org-organization")
            form.fields["project"].queryset = Project.objects.filter(organization=selected_org)
        elif step == "parent":
            selected_org = self.storage.get_step_data("org").get("org-organization")
            form.fields["parent"].queryset = Channel.objects.filter(organization=selected_org, project=None)
        return form

    def get(self, request: "AuthHttpRequest", *args: Any, **kwargs: Any) -> HttpResponse:
        self.extra_context = kwargs.pop("extra_context")
        s: SessionStorage = self.storage
        s.reset()
        s.current_step = self.steps.first
        configured_steps = []
        if "mode" in request.GET:
            s.set_step_data("mode", {"mode-operation": [request.GET.get("mode")]})
            configured_steps.append("mode")

        if "organization" in request.GET:
            if not request.user.organizations.filter(pk=request.GET["organization"]).exists():
                raise PermissionDenied()
            # s.current_step = "prj"
            # s.set_step_data("mode", {"mode-operation": ["new"]})
            s.set_step_data("org", {"org-organization": [request.GET.get("organization")]})
            configured_steps.append("org")
        if "project" in request.GET:
            if not (
                prj := Project.objects.filter(
                    pk=request.GET["project"], organization__in=request.user.organizations
                ).first()
            ):
                raise PermissionDenied()
            s.set_step_data("org", {"org-organization": [prj.organization.pk]})
            s.set_step_data("prj", {"prj-project": [prj.pk]})
            configured_steps.append("org")
            configured_steps.append("prj")

        if configured_steps:
            for step, frm in self.__class__.form_list:  # pragma: no branch
                if frm.visible(self) and step not in configured_steps:
                    s.current_step = step
                    break
        return self.render(self.get_form(s.current_step))

    def post(self, *args: Any, **kwargs: Any) -> HttpResponse:
        self.extra_context = kwargs.pop("extra_context")
        wizard_cancel = self.request.POST.get("wizard_cancel", -1)
        if wizard_cancel != -1:
            if url_has_allowed_host_and_scheme(wizard_cancel, allowed_hosts=None):
                return HttpResponseRedirect(wizard_cancel)
            return HttpResponseRedirect(Channel.get_admin_changelist())
        return super().post(*args, **kwargs)

    def get_current_selection(self) -> dict[str, Any]:  # noqa
        ret = {}
        try:
            ret["mode"]: str = self.storage.get_step_data("mode").get("mode-operation")
            ret["operation"] = dict(ChannelType.MODE_CHOICES)[ret["mode"]]
        except Exception:
            ret["mode"] = None
            ret["operation"] = None
        try:
            ret["organization"] = Organization.objects.get(pk=self.storage.get_step_data("org").get("org-organization"))
        except Exception:
            ret["organization"] = None

        try:
            ret["project"] = Project.objects.get(
                pk=self.storage.get_step_data("prj").get("prj-project"), organization__id=ret["organization"].pk
            )
        except Exception:
            ret["project"] = None

        if ret["mode"] == ChannelType.MODE_INHERIT:
            try:
                ret["parent"] = Channel.objects.get(
                    pk=self.storage.get_step_data("parent").get("parent-parent"),
                    organization__id=ret["organization"].pk,
                )
                ret["name"] = self.storage.get_step_data("parent").get("parent-name")
            except Exception:
                ret["parent"] = None
                ret["name"] = None
        else:
            try:
                ret["name"] = self.storage.get_step_data("data").get("data-name")
            except Exception:
                ret["name"] = None

        try:
            ret["dispatcher"] = self.storage.get_step_data("data").get("data-dispatcher")
        except Exception:
            ret["dispatcher"] = None

        return ret

    def get_context_data(self, form: forms.Form, **kwargs: Any) -> dict[str, Any]:
        kwargs.update(**self.extra_context)
        kwargs["data"] = self.storage.data
        kwargs["back_url"] = self.request.GET.get("_from", "")
        kwargs["selection"] = self.get_current_selection()
        kwargs["cleaned_data"] = {
            form_key: self.get_cleaned_data_for_step(form_key)
            for form_key in self.get_form_list()
            if form_key in self.storage.data["step_data"]
        }

        kwargs["data"] = self.storage.data
        return super().get_context_data(form, **kwargs)

    def done(self, form_list: list[forms.Form], **kwargs: Any) -> HttpResponse:
        # data = self.get_all_cleaned_data()
        data = self.get_current_selection()
        if data["mode"] == ChannelType.MODE_TEMPLATE:
            ch = Channel.objects.create(
                name=data["name"],
                dispatcher=data["dispatcher"],
                organization=data["organization"],
                parent=None,
                project=None,
            )
        elif data["mode"] == ChannelType.MODE_NEW:
            ch = Channel.objects.create(
                name=data["name"],
                dispatcher=data["dispatcher"],
                organization=data["organization"],
                parent=None,
                project=data["project"],
            )
        elif data["mode"] == ChannelType.MODE_INHERIT:
            ch = Channel.objects.create(
                name=data["name"],
                parent=data["parent"],
                dispatcher=data["parent"].dispatcher,
                protocol=data["parent"].protocol,
                organization=data["parent"].organization,
                project=data["project"],
            )
        else:  # pragma: no cover
            raise ValueError(data["mode"])
        return HttpResponseRedirect(reverse("admin:bitcaster_channel_configure", args=[ch.id]))


wizard = ChannelWizard.as_view()


class ChannelAdmin(BaseAdmin, TwoStepCreateMixin[Channel], LockMixinAdmin[Channel], VersionAdmin[Channel]):
    search_fields = ("name",)
    list_display = ("name", "organization", "project", "dispatcher_", "active", "locked", "protocol")
    list_filter = (
        ChannelTypeFilter,
        ("organization", LinkedAutoCompleteFilter.factory(parent=None)),
        ("project", LinkedAutoCompleteFilter.factory(parent="organization")),
        "protocol",
        "active",
        "locked",
        # ("dispatcher", ChoicesFieldComboFilter),
    )
    autocomplete_fields = ("organization", "project")
    change_list_template = "admin/reversion_change_list.html"
    change_form_template = "admin/channel/change_form.html"
    form = ChannelChangeForm
    fieldsets = [
        (
            None,
            {"fields": (("name", "active"),)},
        ),
        (
            None,
            {"fields": (("dispatcher", "protocol"),)},
        ),
        (
            "Advanced options",
            {
                # "classes": ["collapse"],
                "fields": ["organization", "project"],
            },
        ),
    ]

    # def get_fieldsets(self, request: HttpRequest, obj: "Optional[AnyModel]" = None) -> "_FieldsetSpec":
    #     return self.fieldsets
    #     if obj.pk:
    #         return [(None, {"fields": (("name"),)})]
    #     else:
    #         return self.fieldsets

    def dispatcher_(self, obj: Channel) -> str:
        return str(obj.dispatcher)

    def get_queryset(self, request: "HttpRequest") -> QuerySet[Channel]:
        return super().get_queryset(request).select_related("project", "organization")

    def add_view(
        self, request: "HttpRequest", form_url: str | None = "", extra_context: dict[str, Any] | None = None
    ) -> HttpResponse:
        ctx = self.get_common_context(request, add=True, title=_("Add Channel"))
        return wizard(request, extra_context=ctx)

    def get_readonly_fields(self, request: "HttpRequest", obj: "AnyModel | None" = None) -> "_ListOrTuple[str]":
        if obj and obj.pk == config.SYSTEM_EMAIL_CHANNEL:
            return ["name", "organization", "project", "parent", "protocol", "locked"]
        return ["parent", "organization", "protocol", "locked", "project"]

    @link(change_form=True, change_list=False)
    def events(self, button: ButtonWidget) -> None:
        url = reverse("admin:bitcaster_event_changelist")
        ch: Channel = button.context["original"]
        button.href = f"{url}?channels__exact={ch.pk}"

    @button(html_attrs={"class": ButtonColor.ACTION.value})
    def configure(self, request: "HttpRequest", pk: str) -> "HttpResponse":
        obj = self.get_object_or_404(request, pk)
        context = self.get_common_context(request, pk, title=_("Configure channel"))
        form_class = obj.dispatcher.config_class
        if request.method == "POST":
            config_form = form_class(request.POST)
            if config_form.is_valid():
                obj.config = config_form.cleaned_data
                obj.save()
                self.message_user(request, f"Configured channel {obj.name}")
                return HttpResponseRedirect("..")
        else:
            config_form = form_class(initial={k: v for k, v in obj.config.items() if k in form_class.declared_fields})
        fs = (("", {"fields": form_class.declared_fields}),)
        context["admin_form"] = AdminForm(config_form, fs, {})  # type: ignore[arg-type]
        return TemplateResponse(request, "admin/channel/configure.html", context)

    @button(html_attrs={"class": ButtonColor.ACTION.value})
    def test(self, request: "AuthHttpRequest", pk: str) -> "HttpResponse":
        from bitcaster.models import Event

        ch: Channel = self.get_object_or_404(request, pk)
        user: User = request.user
        assignment: Assignment | None = user.get_assignment_for_channel(ch)
        context = self.get_common_context(request, pk, title=_("Test channel"))
        if request.method == "POST":
            config_form = ChannelTestForm(request.POST)
            if config_form.is_valid():
                recipient = str(assignment.address.value)
                payload = Payload(
                    message=config_form.cleaned_data["message"],
                    event=Event(),
                    subject=config_form.cleaned_data["subject"],
                )
                try:
                    ch.dispatcher.send(recipient, payload, assignment=assignment)
                    self.message_user(request, f"Message sent to {recipient} via {ch.name}")
                except Exception as e:
                    logger.exception(e)
                    self.message_error_to_user(request, e)
        else:
            config_form = ChannelTestForm(
                initial={
                    "subject": "[TEST] Subject",
                    "message": "aaa",
                }
            )
        context["assignment"] = assignment
        context["form"] = config_form
        return TemplateResponse(request, "admin/channel/test.html", context)
