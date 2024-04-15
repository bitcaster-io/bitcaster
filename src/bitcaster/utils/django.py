import urllib
from typing import TYPE_CHECKING, Any, Optional

from django.db.models import Model
from django.db.models.options import Options
from django.urls import reverse

if TYPE_CHECKING:
    from bitcaster.types.django import AnyModel


def url_related(m: type[Model], **kwargs: Optional[Any]) -> str:
    opts: "Options[AnyModel]" = m._meta
    base_url = reverse(f"admin:{opts.app_label}_{opts.model_name}_changelist")
    return f"{base_url}?{urllib.parse.urlencode(kwargs)}"
