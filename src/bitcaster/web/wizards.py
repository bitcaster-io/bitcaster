from typing import TYPE_CHECKING, Any, Optional

from django import forms
from django.db.models import QuerySet
from django.http import HttpResponse
from django.shortcuts import render
from formtools.wizard.views import CookieWizardView

from bitcaster.forms import locking as locking_forms
from bitcaster.models import Application, Channel, User

if TYPE_CHECKING:
    from bitcaster.types.http import AuthHttpRequest


class LockingWizard(CookieWizardView):
    form_list = [
        ("mode", locking_forms.ModeChoiceForm),
        ("channel", locking_forms.LockingChannelForm),
        ("project", locking_forms.LockingProjectForm),
        ("application", locking_forms.LockingApplicationForm),
        ("user", locking_forms.LockingUserForm),
        # ("cc", myapp.forms.CreditCardForm),
        # ("confirmation", myapp.forms.OrderForm)
    ]
    condition_dict = {
        "channel": locking_forms.LockingChannelForm.visible,
        "project": locking_forms.LockingProjectForm.visible,
        "application": locking_forms.LockingApplicationForm.visible,
        "user": locking_forms.LockingUserForm.visible,
        # "parent": ChannelSelectParent.visible,
        # "data": ChannelData.visible,
    }
    template_name = "bitcaster/locking/lock.html"

    # def get_template_names(self) -> str:
    #     return TEMPLATES.get(self.steps.current, super().get_template_names())

    def get(self, request: "AuthHttpRequest", *args: Any, **kwargs: Any) -> HttpResponse:
        # self.extra_context = kwargs.pop("extra_context", {})
        return super().get(request, *args, **kwargs)

    def get_form_kwargs(self, step: Optional[str] = None) -> dict[str, Any]:
        kwargs = super().get_form_kwargs(step)
        return kwargs | {"storage": self.storage.data}

    def get_context_data(self, form: forms.Form, **kwargs: Any) -> dict[str, Any]:
        ctx = self.extra_context or {}
        ctx["step_header"] = getattr(self.form_list[self.steps.current], "step_header", "")
        kwargs.update(**ctx)
        return super().get_context_data(form, **kwargs)

    def done(self, form_list: Any, **kwargs: Any) -> HttpResponse:
        data = self.get_all_cleaned_data()
        ctx: dict[str, Any] = {}
        objects: QuerySet[Channel] | QuerySet[Application] | QuerySet[User] | User
        match data["operation"]:
            case locking_forms.LockingModeChoice.CHANNEL:
                objects = data["channel"]
                ctx["title"] = "channels"
            case locking_forms.LockingModeChoice.PROJECT:
                objects = data["application"]
                if not objects:
                    objects = Application.objects.filter(locked=False, project=data["project"]).all()
                ctx["title"] = "applications"
            case locking_forms.LockingModeChoice.USER:
                objects = data["user"]
                ctx["title"] = "users"
            case _:  # pragma: no cover
                raise ValueError("Unexpected operation")

        if hasattr(objects, "id"):
            objects = objects.__class__.objects.filter(id=objects.id)
        ctx["objects"] = list(objects)
        objects.update(locked=True)
        return render(self.request, "bitcaster/locking/done.html", ctx)
