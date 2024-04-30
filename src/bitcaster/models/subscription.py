import logging
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from ..dispatchers.base import Dispatcher, Payload
from .channel import Channel
from .event import Event
from .validation import Validation

if TYPE_CHECKING:
    from bitcaster.types.core import YamlPayload

    from .address import Address
    from .message import Message

logger = logging.getLogger(__name__)


class SubscriptionQuerySet(models.QuerySet["Subscription"]):

    def match(self, payload: Dict[str, Any], rules: "YamlPayload" = None) -> List["Subscription"]:
        for subscription in self.all():
            if subscription.match_filter(payload, rules=rules):
                yield subscription


class Subscription(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="subscriptions")
    # validation = models.ForeignKey(
    #     Validation, blank=True, null=True, on_delete=models.CASCADE, related_name="subscriptions"
    # )

    active = models.BooleanField(default=True)
    hidden = models.BooleanField(default=False, help_text=_("Do not show this subscription in the informative page"))

    objects = SubscriptionQuerySet.as_manager()
    cache = {}

    def __str__(self) -> str:
        return f"{self.validation.address.user}[{self.validation.address}] -> {self.event}"

    class Meta:
        verbose_name = _("Subscription")
        verbose_name_plural = _("Subscriptions")

    def clean(self):
        if not self.distribution and not self.validation:
            raise ValidationError(_("You must specify a distribution or validation."))

    def _distribution_notify(self, context: Dict[str, Any]):
        for validation in self.distribution.recipients.all():
            self._vadidation_notify(validation, context)

    def _validdation_notify(self, validation: "Validation", context: Dict[str, Any]):
        message: Optional["Message"]
        ch: Channel = validation.channel
        addr: "Address" = validation.address

        dispatcher: "Dispatcher" = ch.dispatcher
        if message := self.event.get_message(ch):
            context.update({"channel": ch, "address": addr.value})
            payload: Payload = Payload(
                event=self.event,
                user=self.validation.address.user,
                message=message.render(context),
            )
            dispatcher.send(addr.value, payload)
