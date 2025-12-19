import urllib
from typing import TYPE_CHECKING, Any

from django.conf import settings
from django.db.models import F, Model, QuerySet
from django.http import HttpRequest
from django.urls import reverse

from bitcaster.models import LogEntry

if TYPE_CHECKING:
    from django.db.models.options import Options

    from bitcaster.types.django import AnyModel_co


def get_cache_prefix() -> str:
    return f":{settings.CACHES['default'].get('VERSION', 1)}:"


def url_related(m: type[Model], op: str = "changelist", **kwargs: Any | None) -> str:
    opts: "Options[AnyModel_co]" = m._meta
    base_url = reverse(f"admin:{opts.app_label}_{opts.model_name}_{op}")
    return f"{base_url}?{urllib.parse.urlencode(kwargs)}"


def admin_toggle_bool_action(
    request: HttpRequest, queryset: QuerySet[Model], field: str, message: str | None = None
) -> None:
    queryset.update(**{field: ~F(field)})
    message = message or f"Toggled {field} flag"
    LogEntry.objects.log_actions(request.user.pk, queryset, LogEntry.CHANGE, message)
