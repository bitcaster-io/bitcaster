from typing import TYPE_CHECKING, Any, Optional, List

from django import forms
from django.http import HttpResponse
from django.shortcuts import render
from formtools.wizard.views import CookieWizardView

from bitcaster.forms import locking as locking_forms

if TYPE_CHECKING:
    from bitcaster.types.http import AuthHttpRequest

TEMPLATES = {
    "mode": "bitcaster/locking/mode.html",
    "channel": "bitcaster/locking/channel.html",
    "project": "bitcaster/locking/project.html",
    "user": "bitcaster/locking/user.html",
    # "paytype": "checkout/paymentmethod.html",
    # "cc": "checkout/creditcard.html",
    # "confirmation": "checkout/confirmation.html"
}


class LockingWizard(CookieWizardView):
    form_list = [
        ("mode", locking_forms.ModeChoiceForm),
        ("channel", locking_forms.LockingChannelForm),
        ("project", locking_forms.LockingProjectForm),
        ("user", locking_forms.LockingUserForm),
        # ("cc", myapp.forms.CreditCardForm),
        # ("confirmation", myapp.forms.OrderForm)
    ]
    condition_dict = {
        "channel": locking_forms.LockingChannelForm.visible,
        "project": locking_forms.LockingProjectForm.visible,
        "user": locking_forms.LockingUserForm.visible,
        # "parent": ChannelSelectParent.visible,
        # "data": ChannelData.visible,
    }
    template_name = "bitcaster/locking/mode.html"

    def get_template_names(self) -> str:
        return TEMPLATES.get(self.steps.current, super().get_template_names())

    def get(self, request: "AuthHttpRequest", *args: Any, **kwargs: Any) -> HttpResponse:
        # self.extra_context = kwargs.pop("extra_context", {})
        return super().get(request, *args, **kwargs)

    def get_form_kwargs(self, step: Optional[str] = None) -> dict[str, Any]:
        return super().get_form_kwargs(step)

    def get_form(self, step: Optional[str] = None, data: Any = None, files: Any = None) -> forms.Form:
        form = super().get_form(step, data, files)
        return form

    def get_context_data(self, form: forms.Form, **kwargs: Any) -> dict[str, Any]:
        ctx = self.extra_context or {}
        ctx["step_header"] = getattr(self.form_list[self.steps.current], "step_header", "")
        # if self.steps.current == "channel":
        #     ctx.update({"channel_form": LockingChannelForm()})
        #     channels = Channel.objects.filter(parent__isnull=False).all()
        #     ctx.update({"channels": channels})
        kwargs.update(**ctx)
        return super().get_context_data(form, **kwargs)

    def done(self, form_list, form_dict, **kwargs) -> HttpResponse:
        return render(
            self.request,
            "locking/done.html",
            {
                "form_data": [form.cleaned_data for form in form_list],
            },
        )
