import logging
from typing import TYPE_CHECKING, Any, Optional

from admin_extra_buttons.decorators import button
from adminfilters.autocomplete import LinkedAutoCompleteFilter
from constance import config
from django import forms
from django.contrib.admin.helpers import AdminForm
from django.core.exceptions import PermissionDenied
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.translation import gettext as _
from formtools.wizard.storage.session import SessionStorage
from formtools.wizard.views import CookieWizardView
from reversion.admin import VersionAdmin

from bitcaster.models import Assignment, Channel, Organization, Project, User

from ..dispatchers.base import Payload, dispatcherManager
from ..forms.channel import ChannelChangeForm
from .base import BaseAdmin, ButtonColor
from .mixins import LockMixinAdmin, TwoStepCreateMixin

if TYPE_CHECKING:
    from django.utils.datastructures import _ListOrTuple

    from bitcaster.types.django import AnyModel
    from bitcaster.types.http import AuthHttpRequest

logger = logging.getLogger(__name__)


class ChannelTestForm(forms.Form):
    subject = forms.CharField(required=False)
    message = forms.CharField(widget=forms.Textarea)


class ChannelOrg(forms.Form):
    help_text = _(
        """
Select the organization that this channel belongs to.
    """
    )
    organization = forms.ModelChoiceField(queryset=Organization.objects.all())

    @staticmethod
    def visible(w: "ChannelWizard") -> bool:
        # if (d := w.get_cleaned_data_for_step("mode")) and d["operation"] == "inherit":
        #     return False
        return True


class ChannelProject(forms.Form):
    help_text = _(
        """
Choose the specific project that this channel belongs to.
    """
    )
    project = forms.ModelChoiceField(required=True, queryset=Project.objects.all())

    @staticmethod
    def visible(w: "ChannelWizard") -> bool:
        if w.get_selected_mode() in ["inherit", "new"]:
            return True
        return False


class ChannelType(forms.Form):
    MODE_NEW = "new"
    MODE_INHERIT = "inherit"
    MODE_TEMPLATE = "template"
    help_text = _(
        """
Select the type of channel you want to create. see [[doc:help/channel:Channel]]
    """
    )
    operation = forms.ChoiceField(
        choices=(
            (MODE_NEW, _("Create New Project Channel")),
            (MODE_INHERIT, _("Enable Organization Channel")),
            (MODE_TEMPLATE, _("Create Organization ChannelTemplate")),
        ),
        widget=forms.RadioSelect,
    )

    @staticmethod
    def visible(w: "ChannelWizard") -> bool:
        if w.request and "organization" in w.request.GET:
            return False
        return True


class ChannelSelectParent(forms.ModelForm[Channel]):
    help_text = _(
        """
    """
    )
    parent = forms.ModelChoiceField(queryset=Channel.objects.all(), required=True)

    class Meta:
        model = Channel
        fields = (
            "parent",
            "name",
            # "project",
        )

    @staticmethod
    def visible(w: "ChannelWizard") -> bool:
        if w.get_selected_mode() == ChannelType.MODE_INHERIT:
            # if (d := w.get_cleaned_data_for_step("mode")) and d["operation"] == "inherit":
            return True
        return False


class ChannelData(forms.ModelForm[Channel]):
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
        if w.get_selected_mode() in [ChannelType.MODE_TEMPLATE, ChannelType.MODE_NEW]:
            # if (d := w.get_cleaned_data_for_step("mode")) and d["operation"] == "new":
            return True
        return False


class ManagementForm(forms.Form):
    prefix = "mng"
    current_step = forms.IntegerField()


class ChannelWizard(CookieWizardView):
    form_list = (
        ("mode", ChannelType),
        ("org", ChannelOrg),
        ("prj", ChannelProject),
        ("parent", ChannelSelectParent),
        ("data", ChannelData),
    )
    condition_dict = {
        # "mode": ChannelType.visible,
        "prj": ChannelProject.visible,
        "parent": ChannelSelectParent.visible,
        "data": ChannelData.visible,
    }
    template_name = "admin/channel/add_view.html"

    def get_selected_mode(self) -> Optional[str]:
        if "mode" in self.storage.data.get("step_data"):
            return self.storage.get_step_data("mode")["mode-operation"]
        return None

    def get_form_kwargs(self, step: Optional[str] = None) -> dict[str, Any]:
        return super().get_form_kwargs(step)

    def get_form(self, step: Optional[str] = None, data: Any = None, files: Any = None) -> forms.Form:
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
            return HttpResponseRedirect(wizard_cancel or reverse("admin:bitcaster_channel_changelist"))
        return super().post(*args, **kwargs)

    def get_context_data(self, form: forms.Form, **kwargs: Any) -> dict[str, Any]:
        kwargs.update(**self.extra_context)
        kwargs["data"] = self.storage.data
        kwargs["back_url"] = self.request.GET.get("_from", "")
        kwargs["cleaned_data"] = {
            form_key: self.get_cleaned_data_for_step(form_key)
            for form_key in self.get_form_list()
            if form_key in self.storage.data["step_data"].keys()
        }

        kwargs["data"] = self.storage.data
        return super().get_context_data(form, **kwargs)

    def done(self, form_list: list[forms.Form], **kwargs: Any) -> HttpResponse:
        data = self.get_all_cleaned_data()
        if self.get_selected_mode() == ChannelType.MODE_TEMPLATE:
            ch = Channel.objects.create(
                name=data["name"],
                dispatcher=data["dispatcher"],
                organization=data["organization"],
                parent=None,
                project=None,
            )
        elif self.get_selected_mode() == ChannelType.MODE_NEW:
            ch = Channel.objects.create(
                name=data["name"],
                dispatcher=data["dispatcher"],
                organization=data["organization"],
                parent=None,
                project=data["project"],
            )
        elif self.get_selected_mode() == ChannelType.MODE_INHERIT:
            ch = Channel.objects.create(
                name=data["name"],
                parent=data["parent"],
                dispatcher=data["parent"].dispatcher,
                protocol=data["parent"].protocol,
                organization=data["parent"].organization,
                project=data["project"],
            )
        else:  # pragma: no cover
            raise ValueError(self.get_selected_mode())
        return HttpResponseRedirect(reverse("admin:bitcaster_channel_configure", args=[ch.id]))


wizard = ChannelWizard.as_view()


class ChannelAdmin(BaseAdmin, TwoStepCreateMixin[Channel], LockMixinAdmin[Channel], VersionAdmin[Channel]):
    search_fields = ("name",)
    list_display = ("name", "organization", "project", "dispatcher_", "active", "locked", "protocol")
    list_filter = (
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
        self, request: "HttpRequest", form_url: Optional[str] = "", extra_context: Optional[dict[str, Any]] = None
    ) -> HttpResponse:
        ctx = self.get_common_context(request, add=True, title=_("Add Channel"))
        return wizard(request, extra_context=ctx)

    def get_readonly_fields(self, request: "HttpRequest", obj: "Optional[AnyModel]" = None) -> "_ListOrTuple[str]":
        if obj and obj.pk == config.SYSTEM_EMAIL_CHANNEL:
            return ["name", "organization", "project", "parent", "protocol", "locked"]
        return ["parent", "organization", "protocol", "locked", "project"]

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
                self.message_user(request, "Configured channel {}".format(obj.name))
                return HttpResponseRedirect("..")
        else:
            config_form = form_class(initial={k: v for k, v in obj.config.items() if k in form_class.declared_fields})
        fs = (("", {"fields": form_class.declared_fields}),)
        context["admin_form"] = AdminForm(config_form, fs, {})  # type: ignore[arg-type]
        return TemplateResponse(request, "admin/channel/configure.html", context)

    @button()
    def test(self, request: "AuthHttpRequest", pk: str) -> "HttpResponse":
        from bitcaster.models import Event

        ch: Channel = self.get_object_or_404(request, pk)
        user: User = request.user
        assignment: Optional[Assignment] = user.get_assignment_for_channel(ch)
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
                    self.message_user(request, "Message sent to {} via {}".format(recipient, ch.name))
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
