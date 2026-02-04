from datetime import datetime, timedelta
from typing import TYPE_CHECKING

import constance
from django import template
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from bitcaster.models.attachment import Attachment
from bitcaster.utils.attachment import DownloadKeyManager

if TYPE_CHECKING:
    from bitcaster.models.event import Event

register = template.Library()


class UnrelatedEventError(Exception):
    pass


@register.simple_tag(takes_context=True)
def attachment(context: template.Context, correlation_id: str) -> str:
    """Return the URL for the safe download of an attachment.

    The resulting URL contains a download key which depends on the
    attachment's `correlation_id` and an optional `validity` in
    minutes provided in the message template's context.

    If given, `validity` must be a number greater than or equal to 0.
    An error will be raised otherwise.

    A validity of 0 or `None` means that the key never expires.

    The URL is returned in plain text to ensure compatibility with all
    dispatchers. The user should wrap the URL in the appropriate markup
    for the dispatcher they are using.

    :param context: the message template's context
    :param correlation_id: the correlation ID of the attachment
    :raises ValueError: a negative validity was provided
    :return: the download URL for the attachment in plain text
    """
    attachment = Attachment.objects.get(correlation_id=correlation_id)
    target_event: Event | None = context.get("event")
    if target_event and attachment.application != target_event.application:
        raise UnrelatedEventError(
            _("This attachment is not related to application '{}'").format(target_event.application.name)
        )

    # XXX: can we validate validity before evaluating the tag?
    validity_minutes = context.get("validity")
    if validity_minutes is None or validity_minutes == 0:
        expiration = None
    elif isinstance(validity_minutes, int) and validity_minutes > 0:
        expiration = datetime.now() + timedelta(minutes=validity_minutes)
    else:
        raise ValueError(_("Validity must be zero or greater"))

    base_url = constance.config.ATTACHMENT_BASE_URL
    key = DownloadKeyManager().generate_key(attachment, expiration)

    return base_url + reverse("safe_download", kwargs={"key": key})
