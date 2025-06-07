import urllib
from typing import TYPE_CHECKING, Any

from django.db.models import Model
from django.urls import reverse

if TYPE_CHECKING:
    from django.db.models.options import Options

    from bitcaster.types.django import AnyModel


def url_related(m: type[Model], op: str = "changelist", **kwargs: Any | None) -> str:
    opts: "Options[AnyModel]" = m._meta
    base_url = reverse(f"admin:{opts.app_label}_{opts.model_name}_{op}")
    return f"{base_url}?{urllib.parse.urlencode(kwargs)}"
