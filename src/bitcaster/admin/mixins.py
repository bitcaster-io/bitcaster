from admin_extra_buttons.decorators import button
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.utils.translation import gettext as _

from .base import BUTTON_COLOR_LOCK, BUTTON_COLOR_UNLOCK


class LockMixin:

    @button(
        label=_("Lock"),
        visible=lambda s: not s.context["original"].locked,
        html_attrs={"style": f"background-color:{BUTTON_COLOR_LOCK}"},
    )
    def lock(self, request: "HttpRequest", pk: str) -> "HttpResponse":
        obj = self.get_object(request, pk)
        label = obj._meta.verbose_name
        context = self.get_common_context(request, pk, title=_("Lock {}").format(label), target=label)
        if request.method == "POST":
            obj.locked = True
            obj.save()
            self.message_user(request, _("{} locked").format(label))
            return HttpResponseRedirect("..")
        return TemplateResponse(request, "admin/channel/lock.html", context)

    @button(
        label=_("Unlock"),
        visible=lambda s: s.context["original"].locked,
        html_attrs={"style": f"background-color:{BUTTON_COLOR_UNLOCK}"},
    )
    def unlock(self, request: "HttpRequest", pk: str) -> "HttpResponse":
        obj = self.get_object(request, pk)
        label = obj._meta.verbose_name
        context = self.get_common_context(request, pk, title=_("Unlock {}").format(label), target=label)
        if request.method == "POST":
            obj = self.get_object(request, pk)
            obj.locked = False
            obj.save()
            self.message_user(request, _("{} unlocked").format(label))
            return HttpResponseRedirect("..")
        return TemplateResponse(request, "admin/channel/lock.html", context)
