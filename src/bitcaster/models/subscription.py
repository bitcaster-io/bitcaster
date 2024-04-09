import logging
from typing import TYPE_CHECKING, Any, Dict, Optional

import jmespath
import yaml
from django.db import models
from django.utils.translation import gettext_lazy as _

from ..dispatchers.base import Dispatcher, Payload
from .auth import User
from .channel import Channel
from .event import Event

if TYPE_CHECKING:
    from .message import Message

JsonPayload = Optional[Dict[str, Any] | str]

logger = logging.getLogger(__name__)


class SubscriptionManager(models.Manager["Subscription"]):
    pass


class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="subscriptions")
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="subscriptions")
    channels = models.ManyToManyField(Channel, related_name="subscriptions")
    payload_filter = models.TextField(blank=True, null=True)

    active = models.BooleanField(default=True)

    objects = SubscriptionManager()

    class Meta:
        verbose_name = _("Subscription")
        verbose_name_plural = _("Subscriptions")

    def notify(self, context: Dict[str, Any]) -> None:
        message: Optional["Message"]
        context.update({"subscription": self, "event": self.event})
        for ch in self.channels.active():
            dispatcher: "Dispatcher" = ch.dispatcher
            if addr := self.user.addresses.filter(validations__validated=True, validations__channel=ch).first():
                if message := self.event.messages.filter(channel=ch).first():
                    context.update({"channel": ch, "address": addr})
                    payload: Payload = Payload(
                        event=self.event,
                        channel=ch,
                        user=self.user,
                        message=message.render(context),
                    )
                    dispatcher.send(addr.value, payload)

    @staticmethod
    def match_filter_impl(filter_rules_dict: JsonPayload, payload: JsonPayload, check_only: bool = False) -> bool:
        if not filter_rules_dict:
            return True

        if isinstance(filter_rules_dict, str):
            # this is a leaf, apply the filter
            if check_only:
                return jmespath.compile(filter_rules_dict)
            else:
                return bool(jmespath.search(filter_rules_dict, payload))

        # it is not a str hence it must be a dict with one of AND, OR, NOT
        if and_stm := filter_rules_dict.get("AND"):
            return all([Subscription.match_filter_impl(rules, payload) for rules in and_stm])
        elif or_stm := filter_rules_dict.get("OR"):
            return any([Subscription.match_filter_impl(rules, payload) for rules in or_stm])
        elif not_stm := filter_rules_dict.get("NOT"):
            return not not_stm
        return False

    def match_filter(self, payload: JsonPayload, rules: Optional[Dict[str, Any] | str] = None) -> bool:
        """Check if given payload matches rules.

        If no rules are specified, it defaults to match rules configured in subscription.
        """
        if not rules:
            rules = yaml.safe_load(self.payload_filter or "")
        return Subscription.match_filter_impl(rules, payload)
