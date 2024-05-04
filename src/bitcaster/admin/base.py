import enum
import logging
from typing import TYPE_CHECKING

from admin_extra_buttons.mixins import ExtraButtonsMixin
from adminfilters.mixin import AdminAutoCompleteSearchMixin, AdminFiltersMixin
from django.db.models import QuerySet
from django.http import HttpRequest

if TYPE_CHECKING:
    from bitcaster.types.django import AnyModel

logger = logging.getLogger(__name__)


class ButtonColor(enum.Enum):
    LINK = "#96AA86"
    ACTION = "#2B44D6"
    LOCK = "#ba2121"
    UNLOCK = "green"


class BaseAdmin(AdminFiltersMixin, AdminAutoCompleteSearchMixin, ExtraButtonsMixin):
    def get_search_results(
        self, request: HttpRequest, queryset: "QuerySet[AnyModel]", search_term: str
    ) -> "tuple[QuerySet[AnyModel], bool]":
        field_names = [f.name for f in self.model._meta.get_fields()]
        filters = {k: v for k, v in request.GET.items() if k in field_names}
        exclude = {k[:-5]: v for k, v in request.GET.items() if k.endswith("__not") and k[:-5] in field_names}
        queryset = queryset.filter(**filters).exclude(**exclude)
        queryset, may_have_duplicates = super().get_search_results(request, queryset, search_term)
        return queryset, may_have_duplicates
