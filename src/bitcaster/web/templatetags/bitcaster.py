from unfold.templatetags.unfold import header_title

from django import template
from django.core.signing import Signer
from django.template import Context, RequestContext
from django.template.loader import render_to_string

from bitcaster.models import Channel, Notification, Occurrence
from bitcaster.utils.http import absolute_reverse
from bitcaster.utils.security import KeyManager

register = template.Library()

signer = Signer()


@register.simple_tag(takes_context=True)
def bc_header_title(context: RequestContext) -> str:
    breadcrumbs: list[str] | None
    parts: list[dict[str, str]] = []
    if breadcrumbs := context.get("breadcrumbs"):
        parts.extend(
            {
                "link": breadcrumb[0],
                "title": breadcrumb[1],
            }
            for breadcrumb in breadcrumbs
        )
        return render_to_string(
            "unfold/helpers/header_title.html",
            request=context.request,
            context={
                "parts": parts,
            },
        )
    return header_title(context)


@register.simple_tag(takes_context=True)
def recipients(
    context: Context,
    occurrence: Occurrence,
    channel: Channel | None = None,
    notification: Notification | None = None,
) -> str:
    parts = {"occurrence": occurrence.pk, "address": context["address"]}
    if notification:
        parts["notification"] = notification.pk
    elif channel:
        parts["channel"] = channel.pk
    key = KeyManager().generate_key(ttl=5, **parts)
    return absolute_reverse("recipients", args=[key])
