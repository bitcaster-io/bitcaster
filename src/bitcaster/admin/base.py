import enum
import logging
from typing import TYPE_CHECKING, Any, Generic

from admin_extra_buttons.mixins import ExtraButtonsMixin
from adminfilters.mixin import AdminAutoCompleteSearchMixin, AdminFiltersMixin
from django.http import Http404, HttpRequest, HttpResponse, HttpResponseRedirect

from bitcaster.state import state

if TYPE_CHECKING:
    from django.db.models import QuerySet

    from bitcaster.types.django import AnyModel

logger = logging.getLogger(__name__)


class ButtonColor(enum.Enum):
    LINK = "link"
    ACTION = "action"
    LOCK = "lock"
    UNLOCK = "unlock"


class BaseAdmin(AdminFiltersMixin, AdminAutoCompleteSearchMixin, ExtraButtonsMixin):
    def get_object_or_404(self, request: HttpRequest, object_id: str, from_field: str | None = None) -> "AnyModel":
        if not (ret := self.get_object(request, object_id, from_field)):
            raise Http404
        return ret

    def response_add(
        self, request: HttpRequest, obj: "Generic[AnyModel]", post_url_continue: str | None = None
    ) -> HttpResponse:
        ret = super().response_add(request, obj, post_url_continue)
        # if ret.status_code in [200, 400]:
        #     return ret
        if redirect_url := request.GET.get("next", ""):
            return HttpResponseRedirect(redirect_url)
        return ret

    def get_search_results(
        self, request: HttpRequest, queryset: "QuerySet[AnyModel]", search_term: str
    ) -> "tuple[QuerySet[AnyModel], bool]":
        field_names = [f.name for f in self.model._meta.get_fields()]
        filters = {k: v for k, v in request.GET.items() if k in field_names}
        exclude = {k[:-5]: v for k, v in request.GET.items() if k.endswith("__not") and k[:-5] in field_names}
        queryset = queryset.filter(**filters).exclude(**exclude)
        queryset, may_have_duplicates = super().get_search_results(request, queryset, search_term)
        return queryset, may_have_duplicates

    def get_changeform_initial_data(self, request: HttpRequest) -> dict[str, Any]:
        from bitcaster.models import Organization

        initial = super().get_changeform_initial_data(request)
        initial.setdefault("user", request.user.id)
        initial.setdefault("owner", request.user.id)
        initial.setdefault("organization", state.get_cookie("organization") or Organization.objects.local().first())
        initial.setdefault("project", state.get_cookie("project"))
        initial.setdefault("application", state.get_cookie("application"))
        return initial

    def changeform_view(
        self,
        request: HttpRequest,
        object_id: str | None = None,
        form_url: str = "",
        extra_context: dict[str, Any] | None = None,
    ) -> HttpResponse:
        extra_context = extra_context or {}

        # extra_context["show_save"] = True
        extra_context["show_save_and_add_another"] = False
        extra_context["show_save_and_continue"] = self.save_as_continue

        return super().changeform_view(request, object_id, form_url, extra_context)
