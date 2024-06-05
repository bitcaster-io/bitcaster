from typing import Any, Optional

from django import forms
from django.http import HttpResponse
from django.shortcuts import render
from formtools.wizard.views import CookieWizardView

from bitcaster.forms import locking as locking_forms
from bitcaster.models import Channel
from bitcaster.types.http import AuthHttpRequest

TEMPLATES = {
    "mode": "bitcaster/locking/mode.html",
    "step1C": "bitcaster/locking/step1C.html",
    # "paytype": "checkout/paymentmethod.html",
    # "cc": "checkout/creditcard.html",
    # "confirmation": "checkout/confirmation.html"
}


class LockingWizard(CookieWizardView):
    form_list = [
        ("mode", locking_forms.ModeChoiceForm),
        ("channel", locking_forms.LockingChannelForm),
        ("step1P", locking_forms.ModeChoiceForm),
        ("step1U", locking_forms.ModeChoiceForm),
        # ("cc", myapp.forms.CreditCardForm),
        # ("confirmation", myapp.forms.OrderForm)
    ]
    condition_dict = {
        # "org": ChannelOrg.visible,
        # "prj": ChannelProject.visible,
        # "parent": ChannelSelectParent.visible,
        # "data": ChannelData.visible,
    }
    template_name = "bitcaster/locking/mode.html"

    def get_template_names(self) -> str:
        return {
            "channel": "bitcaster/locking/channel.html",
        }.get(self.steps.current, super().get_template_names())

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
        ctx["step_header"] = self.form_list[self.steps.current].step_header
        if self.steps.current == "channel":
            channels = Channel.objects.filter(parent__isnull=False).all()
            ctx.update({"channels": channels})
        kwargs.update(**ctx)
        return super().get_context_data(form, **kwargs)

    def done(self, form_list, form_dict, **kwargs):
        return render(
            self.request,
            "locking/done.html",
            {
                "form_data": [form.cleaned_data for form in form_list],
            },
        )
