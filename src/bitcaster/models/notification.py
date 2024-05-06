from typing import TYPE_CHECKING, Any, Optional

import jmespath
import yaml
from django.db import models
from django.db.models import QuerySet

from ..dispatchers.base import Payload
from .distribution import DistributionList
from .validation import Validation

if TYPE_CHECKING:
    from bitcaster.dispatchers.base import Dispatcher
    from bitcaster.models import Address, Channel, Message
    from bitcaster.types.core import YamlPayload


class NotificationQuerySet(models.QuerySet["Notification"]):

    def match(self, payload: dict[str, Any], rules: "Optional[YamlPayload]" = None) -> list["Notification"]:
        for subscription in self.all():
            if subscription.match_filter(payload, rules=rules):
                yield subscription


class Notification(models.Model):
    name = models.CharField(max_length=100)
    event = models.ForeignKey("bitcaster.Event", on_delete=models.CASCADE, related_name="notifications")
    distribution = models.ForeignKey(
        DistributionList, blank=True, null=True, on_delete=models.CASCADE, related_name="notifications"
    )
    payload_filter = models.TextField(blank=True, null=True)
    extra_context = models.JSONField(default=dict)
    objects = NotificationQuerySet.as_manager()

    def __init__(self, *args: Any, **kwargs: Any):
        self._cached_messages: dict[Channel, Message | None] = {}
        super().__init__(*args, **kwargs)

    def __str__(self) -> str:
        return self.name

    def get_context(self, ctx: dict[str, str]) -> dict[str, Any]:
        return {**ctx, "notification": self.name}

    def get_pending_subscriptions(self, delivered: list[str | int], channel: "Channel") -> QuerySet[Validation]:
        return (
            self.distribution.recipients.select_related(
                "address",
                "channel",
                "address__user",
            )
            .filter(active=True, channel=channel)
            .exclude(id__in=delivered)
        )

    def notify_to_channel(self, channel: "Channel", validation: Validation, context: dict[str, Any]) -> Optional[str]:
        message: Optional["Message"]

        dispatcher: "Dispatcher" = channel.dispatcher
        addr: "Address" = validation.address
        if message := self.get_message(channel):
            context.update({"channel": channel, "address": addr.value})
            payload: Payload = Payload(
                event=self.event,
                user=addr.user,
                message=message.render(context),
            )
            dispatcher.send(addr.value, payload)
            return addr.value
        return None

    @classmethod
    def match_line_filter(cls, filter_rules_dict: "YamlPayload", payload: "YamlPayload") -> bool:
        if not filter_rules_dict:
            return True

        if isinstance(filter_rules_dict, str):
            # this is a leaf, apply the filter
            return bool(jmespath.search(filter_rules_dict, payload))

        # it is not a str hence it must be a dict with one of AND, OR, NOT
        if and_stm := filter_rules_dict.get("AND"):
            return all([cls.match_line_filter(rules, payload) for rules in and_stm])
        elif or_stm := filter_rules_dict.get("OR"):
            return any([cls.match_line_filter(rules, payload) for rules in or_stm])
        elif not_stm := filter_rules_dict.get("NOT"):
            return not cls.match_line_filter(not_stm, payload)
        return False

    def match_filter(self, payload: "YamlPayload", rules: Optional[dict[str, Any] | str] = None) -> bool:
        """Check if given payload matches rules.

        If no rules are specified, it defaults to match rules configured in subscription.
        """
        if not rules:
            rules = yaml.safe_load(self.payload_filter or "")
        return self.match_line_filter(rules, payload)

    # @staticmethod
    # def check_filter(filter_rules_dict: "YamlPayload") -> Any:
    #     return jmespath.compile(filter_rules_dict)

    def get_messages(self, channel: "Channel") -> QuerySet["Message"]:
        from .message import Message

        return (
            Message.objects.filter(channel=channel)
            .filter(models.Q(event=self.event, notification=self) | models.Q(event=self.event, notification=None))
            .order_by("notification")
        )

    def get_message(self, channel: "Channel") -> "Optional[Message]":
        if channel not in self._cached_messages:
            ret = self.get_messages(channel).first()
            self._cached_messages[channel] = ret
        return self._cached_messages[channel]

    def create_message(self, name: str, channel: "Channel", defaults: Optional[dict[str, Any]] = None) -> "Message":
        return self.messages.get_or_create(
            name=name,
            channel=channel,
            notification=self,
            event=self.event,
            application=self.event.application,
            project=self.event.application.project,
            organization=self.event.application.project.organization,
            defaults=defaults if defaults else {},
        )[0]
