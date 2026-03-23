from typing import TYPE_CHECKING

from django import template
from django.utils.translation import gettext_lazy as _

from bitcaster.exceptions import UnrelatedEventError
from bitcaster.models.attachment import Attachment
from bitcaster.utils.http import absolute_reverse
from bitcaster.utils.security import KeyManager

if TYPE_CHECKING:
    from bitcaster.models.event import Event

register = template.Library()


@register.simple_tag(takes_context=True)
def attachment(context: template.Context, correlation_id: str, validity: int | None = None) -> str:
    try:
        attachment = Attachment.objects.get(correlation_id=correlation_id)
        target_event: Event | None = context.get("event")
        if target_event and attachment.application != target_event.application:
            raise UnrelatedEventError(
                _("This attachment is not related to application '{}'").format(target_event.application.name)
            )
    except Attachment.DoesNotExist:
        raise Attachment.DoesNotExist(f"Attachment '{correlation_id}' does not exist") from None

    address = context["address"]
    try:
        key = KeyManager().generate_key(validity, correlation_id=correlation_id, address=address)
    except (TypeError, ValueError) as e:
        raise ValueError(_("attachment: TTL must be an integer")) from e

    return absolute_reverse("safe_download", kwargs={"key": key})
