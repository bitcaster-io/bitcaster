from typing import TYPE_CHECKING, Any

from django import template
from django.conf import settings
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _

from ..links import resolve_help_url

if TYPE_CHECKING:
    from django.http import HttpRequest

register = template.Library()


@register.simple_tag(takes_context=True, name="help")
def help_tag(context: dict[str, Any]) -> str:
    request: "HttpRequest | None" = context.get("request")
    if request is None or context.get("is_popup"):
        return ""
    doc_site = settings.BITCASTER_DOCUMENTATION_SITE_URL
    if not doc_site:
        return ""
    url = resolve_help_url(request.path, doc_site)
    if url is None:
        return ""
    label = escape(_("Documentation"))
    return mark_safe(  # nosec: B703 B308  # noqa: S308 - values escaped above, markup is static
        '<a class="block cursor-pointer h-[18px] hover:text-base-700 dark:hover:text-base-200" '
        f'href="{escape(url)}" target="_blank" rel="noopener" '
        f'title="{label}" aria-label="{label}">'
        '<span class="material-symbols-outlined">help</span></a>'
    )
