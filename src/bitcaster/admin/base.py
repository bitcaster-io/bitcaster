from typing import TYPE_CHECKING, Any

import enum
import logging

from admin_extra_buttons.mixins import ExtraButtonsMixin
from adminfilters.mixin import AdminAutoCompleteSearchMixin, AdminFiltersMixin
from smart_selects.db_fields import ChainedForeignKey
from unfold.admin import ModelAdmin as UnfoldModelAdmin  # noqa
from unfold.contrib.forms import widgets as uwidgets

from django.contrib.postgres.fields import ArrayField
from django.db.models import ForeignKey, TextField
from django.forms import ModelChoiceField
from django.http import Http404, HttpRequest, HttpResponse, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.utils.translation import gettext_lazy as _

from bitcaster.forms.unfold import UnfoldChainedSelect
from bitcaster.state import state

if TYPE_CHECKING:  # pragma: no cover
    from django.db.models import QuerySet

logger = logging.getLogger(__name__)


class ButtonColor(enum.Enum):
    LINK = "link"
    ACTION = "action"
    LOCK = "lock"
    UNLOCK = "unlock"


class BitcasterModelAdmin[T](UnfoldModelAdmin):
    warn_unsaved_form = True
    list_filter_submit = True
    formfield_overrides = {
        TextField: {
            "widget": uwidgets.WysiwygWidget,
        },
        ArrayField: {
            "widget": uwidgets.ArrayWidget,
        },
    }

    def has_view_or_change_permission(self, request: HttpRequest, obj: Any = None) -> bool:
        return super().has_view_or_change_permission(request, obj)

    def changelist_view(self, request: HttpRequest, extra_context: dict[str, Any] | None = None) -> TemplateResponse:
        return super().changelist_view(request, extra_context)

    def formfield_for_foreignkey(
        self, db_field: ForeignKey[Any], request: HttpRequest, **kwargs: Any
    ) -> ModelChoiceField[Any] | None:
        if isinstance(db_field, ChainedForeignKey) and db_field.name not in self.get_autocomplete_fields(request):
            widget = UnfoldChainedSelect(
                to_app_name=db_field.to_app_name,
                to_model_name=db_field.to_model_name,
                chained_field=db_field.chained_field,
                chained_model_field=db_field.chained_model_field,
                foreign_key_app_name=db_field.model._meta.app_label,
                foreign_key_model_name=db_field.model._meta.object_name,
                foreign_key_field_name=db_field.name,
                show_all=db_field.show_all,
                auto_choose=db_field.auto_choose,
                sort=db_field.sort,
                view_name=db_field.view_name,
            )
            kwargs["widget"] = widget
        # Overrides widgets for all related fields
        # Note: we do not use raw_id_fields so we slip if db_field.name in self.raw_id_fields:
        if (
            "widget" not in kwargs
            and db_field.name not in self.get_autocomplete_fields(request)
            and db_field.name not in self.radio_fields
        ):
            kwargs["widget"] = uwidgets.UnfoldAdminSelectWidget()
            kwargs["empty_label"] = _("Select value")
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class BaseAdmin[T](
    BitcasterModelAdmin[T],
    AdminFiltersMixin,
    AdminAutoCompleteSearchMixin,
    ExtraButtonsMixin,
):
    def get_object_or_404(self, request: HttpRequest, object_id: str, from_field: str | None = None) -> Any:
        if not (ret := self.get_object(request, object_id, from_field)):
            raise Http404
        return ret

    def response_add(self, request: HttpRequest, obj: Any, post_url_continue: str | None = None) -> HttpResponse:
        ret = super().response_add(request, obj, post_url_continue)
        if redirect_url := request.GET.get("next", ""):
            return HttpResponseRedirect(redirect_url)
        return ret

    def get_search_results(
        self, request: HttpRequest, queryset: "QuerySet[Any]", search_term: str
    ) -> "tuple[QuerySet[Any], bool]":
        field_names = [f.name for f in self.model._meta.get_fields()]
        filters = {k: v for k, v in request.GET.items() if k in field_names}
        exclude = {k[:-5]: v for k, v in request.GET.items() if k.endswith("__not") and k[:-5] in field_names}
        queryset = queryset.filter(**filters).exclude(**exclude)
        queryset, may_have_duplicates = super().get_search_results(request, queryset, search_term)
        return queryset, may_have_duplicates

    def get_changeform_initial_data(self, request: HttpRequest) -> dict[str, Any]:
        from bitcaster.models import Organization

        initial = super().get_changeform_initial_data(request)
        initial.setdefault("user", str(request.user.id))
        initial.setdefault("owner", str(request.user.id))
        org = Organization.objects.local().first()
        initial.setdefault("organization", str(state.get_cookie("organization") or (org.id if org else "")))
        initial.setdefault("project", str(state.get_cookie("project") or ""))
        initial.setdefault("application", str(state.get_cookie("application") or ""))
        return initial

    def changeform_view(
        self,
        request: HttpRequest,
        object_id: str | None = None,
        form_url: str = "",
        extra_context: dict[str, Any] | None = None,
    ) -> HttpResponse:
        extra_context = extra_context or {}

        extra_context.setdefault("show_save_and_add_another", False)
        extra_context.setdefault("show_save_and_continue", self.save_as_continue)

        return super().changeform_view(request, object_id, form_url, extra_context)
