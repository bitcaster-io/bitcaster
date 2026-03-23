from django import template
from django.core.signing import Signer
from django.template import Context

from bitcaster.models import Channel, DistributionList, Occurrence
from bitcaster.utils.http import absolute_reverse
from bitcaster.utils.security import KeyManager

register = template.Library()

signer = Signer()


@register.simple_tag(takes_context=True)
def recipients(
    context: Context,
    occurrence: Occurrence,
    channel: Channel | None = None,
    distribution: DistributionList | None = None,
) -> str:
    parts = {"occurrence": occurrence.pk, "address": context["address"]}
    if distribution:
        parts["distribution"] = distribution.pk
    elif channel:
        parts["channel"] = channel.pk
    key = KeyManager().generate_key(ttl=5, **parts)
    return absolute_reverse("recipients", args=[key])
