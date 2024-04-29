import logging
from typing import TYPE_CHECKING, Any, Dict, List, Optional

import jmespath
import yaml
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from ..dispatchers.base import Dispatcher, Payload
from .channel import Channel
from .distribution import DistributionList
from .event import Event
from .validation import Validation

if TYPE_CHECKING:
    from .address import Address
    from .message import Message

YamlPayload = Optional[Dict[str, Any] | str]

logger = logging.getLogger(__name__)


class SubscriptionQuerySet(models.QuerySet["Subscription"]):

    def match(self, payload: Dict[str, Any], rules: YamlPayload = None) -> List["Subscription"]:
        for subscription in self.all():
            if subscription.match_filter(payload, rules=rules):
                yield subscription


class Subscription(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="subscriptions")
    validation = models.ForeignKey(
        Validation, blank=True, null=True, on_delete=models.CASCADE, related_name="subscriptions"
    )
    distribution = models.ForeignKey(
        DistributionList, blank=True, null=True, on_delete=models.CASCADE, related_name="subscriptions"
    )

    payload_filter = models.TextField(blank=True, null=True)

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

    def notify(self, context: Dict[str, Any]) -> None:
        if self.validation:
            context.update({"subscription": self, "event": self.event})
            self._validdation_notify(self.validation, context)
        else:
            context.update({"event": self.event})
            self._distribution_notify(context)

    @staticmethod
    def match_filter_impl(filter_rules_dict: YamlPayload, payload: YamlPayload) -> bool:
        if not filter_rules_dict:
            return True

        if isinstance(filter_rules_dict, str):
            # this is a leaf, apply the filter
            return bool(jmespath.search(filter_rules_dict, payload))

        # it is not a str hence it must be a dict with one of AND, OR, NOT
        if and_stm := filter_rules_dict.get("AND"):
            return all([Subscription.match_filter_impl(rules, payload) for rules in and_stm])
        elif or_stm := filter_rules_dict.get("OR"):
            return any([Subscription.match_filter_impl(rules, payload) for rules in or_stm])
        elif not_stm := filter_rules_dict.get("NOT"):
            return not Subscription.match_filter_impl(not_stm, payload)
        return False

    def match_filter(self, payload: YamlPayload, rules: Optional[Dict[str, Any] | str] = None) -> bool:
        """Check if given payload matches rules.

        If no rules are specified, it defaults to match rules configured in subscription.
        """
        if not rules:
            rules = yaml.safe_load(self.payload_filter or "")
        return Subscription.match_filter_impl(rules, payload)

    @staticmethod
    def check_filter(filter_rules_dict: YamlPayload):
        return jmespath.compile(filter_rules_dict)
