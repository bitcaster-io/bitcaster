from admin_extra_buttons.decorators import button
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.utils.translation import gettext as _


class LockMixin:

    @button(visible=lambda s: not s.context["original"].locked, html_attrs={"style": "background-color:#ba2121"})
    def lock(self, request: "HttpRequest", pk: str) -> "HttpResponse":
        obj = self.get_object(request, pk)
        label = obj._meta.verbose_name
        context = self.get_common_context(request, pk, title=_("Lock {}").format(label), target=label)
        if request.method == "POST":
            obj.locked = True
            obj.save()
            self.message_user(request, _("{} locked").format(label))
            return HttpResponseRedirect("..")
        return TemplateResponse(request, "bitcaster/admin/channel/lock.html", context)

    @button(visible=lambda s: s.context["original"].locked, html_attrs={"style": "background-color:green"})
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
        return TemplateResponse(request, "bitcaster/admin/channel/lock.html", context)
