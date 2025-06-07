import logging
from typing import TYPE_CHECKING, Any

import jmespath
import yaml
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models import QuerySet
from django.utils.functional import cached_property
from django.utils.translation import gettext as _

from ..dispatchers.base import Payload
from ..utils.shortcuts import render_string
from .assignment import Assignment
from .distribution import DistributionList
from .mixins import BaseQuerySet, BitcasterBaseModel, BitcasterBaselManager

if TYPE_CHECKING:
    from bitcaster.dispatchers.base import Dispatcher
    from bitcaster.models import Address, Application, Channel, Message
    from bitcaster.types.core import YamlPayload

logger = logging.getLogger(__name__)


class NotificationQuerySet(BaseQuerySet["Notification"]):
    def match(self, payload: dict[str, Any], rules: "YamlPayload | None" = None) -> list["Notification"]:
        for subscription in self.all():
            if subscription.match_filter(payload, rules=rules):
                yield subscription

    def get_by_natural_key(self, name: str, evt: str, app: str, prj: str, org: str, *args: Any) -> "Notification":
        return self.get(
            event__application__project__organization__slug=org,
            event__application__project__slug=prj,
            event__application__slug=app,
            event__slug=evt,
            name=name,
        )


class NotificationManager(BitcasterBaselManager.from_queryset(NotificationQuerySet)):
    _queryset_class = NotificationQuerySet


class Notification(BitcasterBaseModel):
    name = models.CharField(max_length=100)
    event = models.ForeignKey("bitcaster.Event", on_delete=models.CASCADE, related_name="notifications")
    distribution = models.ForeignKey(
        DistributionList, blank=True, null=True, on_delete=models.CASCADE, related_name="notifications"
    )
    environments = ArrayField(
        models.CharField(max_length=20, blank=True, null=True),
        blank=True,
        null=True,
        help_text=_("Allow notification only for these environments"),
    )
    payload_filter = models.TextField(blank=True, null=True)
    extra_context = models.JSONField(default=dict, blank=True)

    objects = NotificationManager()

    class Meta:
        verbose_name = _("Notification")
        verbose_name_plural = _("Notifications")
        unique_together = (("event", "name"),)
        constraints = [
            models.UniqueConstraint(
                fields=("event", "name"),
                name="notification_event_name",
            )
        ]

    def natural_key(self) -> tuple[str | None, ...]:
        return self.name, *self.event.natural_key()

    def __init__(self, *args: Any, **kwargs: Any):
        self._cached_messages: dict[Channel, Message | None] = {}
        super().__init__(*args, **kwargs)

    def __str__(self) -> str:
        return self.name

    @cached_property
    def application(self) -> "Application":
        return self.event.application

    def get_context(self, ctx: dict[str, str]) -> dict[str, Any]:
        return {**ctx, "notification": self.name} | self.extra_context

    def get_pending_subscriptions(self, delivered: list[str | int], channel: "Channel") -> QuerySet[Assignment]:
        return (
            self.distribution.recipients.select_related(
                "address",
                "channel",
                "address__user",
            )
            .filter(active=True, channel=channel)
            .exclude(id__in=delivered)
        )

    def notify_to_channel(self, channel: "Channel", assignment: Assignment, context: dict[str, Any]) -> str | None:
        message: "Message" | None
        dispatcher: "Dispatcher" = channel.dispatcher
        addr: "Address" = assignment.address

        logger.debug(f"channel: {channel} , assignment: {assignment} , context: {context}")
        if message := self.get_message(channel):
            logger.debug(f"message: {message}")
            context.update({"channel": channel, "address": addr.value})
            payload: Payload = Payload(
                event=self.event,
                user=addr.user,
                subject=render_string(message.subject, context),
                message=render_string(message.content, context),
                html_message=render_string(message.html_content, context),
                # message=message.render(context),
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
            return all(cls.match_line_filter(rules, payload) for rules in and_stm)
        if or_stm := filter_rules_dict.get("OR"):
            return any(cls.match_line_filter(rules, payload) for rules in or_stm)
        if not_stm := filter_rules_dict.get("NOT"):
            return not cls.match_line_filter(not_stm, payload)
        return False

    def match_filter(self, payload: "YamlPayload", rules: dict[str, Any] | str | None = None) -> bool:
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

    def get_message(self, channel: "Channel") -> "Message | None":
        if channel not in self._cached_messages:
            ret = self.get_messages(channel).first()
            self._cached_messages[channel] = ret
        return self._cached_messages[channel]

    def create_message(self, name: str, channel: "Channel", defaults: dict[str, Any] | None = None) -> "Message":
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
