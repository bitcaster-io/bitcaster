from typing import Any

from admin_extra_buttons.decorators import button
from django.contrib import messages
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.utils.translation import gettext_lazy as _

from .base import BitcasterModelAdmin, ButtonColor


class LockMixinAdmin[T](BitcasterModelAdmin[T]):
    def render_change_form(
        self,
        request: HttpRequest,
        context: dict[str, Any],
        add: bool = False,
        change: bool = False,
        form_url: str = "",
        obj: T | None = None,
    ) -> HttpResponse:
        if obj and getattr(obj, "locked", False):
            self.message_user(request, str(_("Locked")), messages.ERROR)
        return super().render_change_form(request, context, add, change, form_url, obj)

    @button(  # type: ignore[arg-type]
        label=_("Lock"),
        visible=lambda s: not s.context["original"].locked,
        enabled=lambda s: s.context["original"].can_be_locked(),
        permission=lambda r, o, handler: r.user.has_perm("bitcaster.console_lock"),
        html_attrs={"class": ButtonColor.LOCK.value},
    )
    def lock(self, request: HttpRequest, pk: str) -> HttpResponse | None:
        obj = self.get_object(request, pk)
        if obj and obj.can_be_locked():
            label = obj._meta.verbose_name
            context = self.get_common_context(request, pk, title=_("Lock {}").format(label), target=label)
            if request.method == "POST":
                obj.lock()
                self.message_user(request, _("{} locked").format(label))
                return HttpResponseRedirect("..")
            return TemplateResponse(request, "bitcaster/admin/channel/lock.html", context)
        return None

    @button(  # type: ignore[arg-type]
        label=_("Unlock"),
        visible=lambda s: s.context["original"].locked,
        enabled=lambda s: s.context["original"].can_be_locked(),
        permission=lambda r, o, handler: r.user.has_perm("bitcaster.console_lock"),
        html_attrs={"class": ButtonColor.UNLOCK.value},
    )
    def unlock(self, request: HttpRequest, pk: str) -> HttpResponse | None:
        obj = self.get_object(request, pk)
        if obj:
            label = obj._meta.verbose_name
            context = self.get_common_context(request, pk, title=_("Unlock {}").format(label), target=label)
            if request.method == "POST":
                obj.unlock()
                self.message_user(request, _("{} unlocked").format(label))
                return HttpResponseRedirect("..")
            return TemplateResponse(request, "bitcaster/admin/channel/lock.html", context)
        return None


class TwoStepCreateMixin[T]:
    def changeform_view(
        self: Any,
        request: HttpRequest,
        object_id: str | None = None,
        form_url: str = "",
        extra_context: dict[str, Any] | None = None,
    ) -> HttpResponse:
        extra_context = extra_context or {}
        extra_context["show_save_and_continue"] = True
        if object_id is None:
            extra_context["show_save"] = False
        extra_context["show_save_as_new"] = False
        extra_context["show_save_and_add_another"] = False
        return super().changeform_view(request, object_id, form_url=form_url, extra_context=extra_context)
