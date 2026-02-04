import logging
from typing import TYPE_CHECKING, Any, Generator

import jmespath
import yaml
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models import QuerySet
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from ..dispatchers.base import Payload
from ..utils.filtering import FilterManager
from .assignment import Assignment
from .distribution import DistributionList
from .mixins import BaseQuerySet, BitcasterBaseModel, BitcasterBaselManager
from .user import User

if TYPE_CHECKING:
    from bitcaster.dispatchers.base import Dispatcher
    from bitcaster.models import Address, Application, Channel, MessageTemplate
    from bitcaster.types.yaml import YamlPayload

logger = logging.getLogger(__name__)


class NotificationQuerySet(BaseQuerySet["Notification"]):
    def match(self, payload: dict[str, Any], rules: "YamlPayload | None" = None) -> "Generator[Notification]":
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
    name = models.CharField(verbose_name=_("name"), max_length=100)
    event = models.ForeignKey("bitcaster.Event", on_delete=models.CASCADE, related_name="notifications")
    distribution = models.ForeignKey(
        DistributionList, blank=True, null=True, on_delete=models.CASCADE, related_name="notifications"
    )
    environments = ArrayField(
        models.CharField(max_length=20, blank=True, null=True),
        verbose_name=_("environments"),
        blank=True,
        null=True,
        help_text=_("Allow notification only for these environments"),
    )
    payload_filter = models.TextField(verbose_name=_("payload filter"), blank=True, null=True)
    extra_context = models.JSONField(default=dict, blank=True)
    active = models.BooleanField(verbose_name=_("active"), default=False)
    external_filtering = models.BooleanField(
        verbose_name=_("external filtering"),
        default=False,
        help_text="Allow filtering recipients based on rules passed in the api call",
    )

    dynamic = models.BooleanField(
        default=False,
        help_text="Dynamic notification do not need DistributionList. "
        "It filters users based on 'recipients_filter' rules",
    )
    recipients_filter = models.JSONField(
        default=dict,
        blank=True,
    )

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
        self._cached_messages: dict[Channel, MessageTemplate | None] = {}
        super().__init__(*args, **kwargs)

    def __str__(self) -> str:
        return self.name

    @cached_property
    def application(self) -> "Application":
        return self.event.application

    def get_context(self, ctx: dict[str, str]) -> dict[str, Any]:
        ctx = {**ctx, "notification": self.name} | self.extra_context
        if self.distribution:
            ctx.update(self.distribution.get_context())
        return ctx

    def get_pending_subscriptions(
        self, delivered: list[str | int], channel: "Channel", api_filtering: Any
    ) -> QuerySet[Assignment]:
        if self.dynamic and self.recipients_filter:
            included, excluded = FilterManager.parse(self.recipients_filter)
            users = User.objects.filter(included).exclude(excluded)
        elif self.external_filtering and api_filtering:
            included, excluded = FilterManager.parse(api_filtering)
            users = User.objects.filter(included).exclude(excluded)
        else:
            users = User.objects.filter(is_active=True)
        if self.dynamic or self.external_filtering:
            return self.get_dynamic_pending_subscriptions(delivered, channel, filter_users=users)
        return self.get_distributionlist_pending_subscriptions(delivered, channel, filter_users=users)

    def get_dynamic_pending_subscriptions(
        self, delivered: list[str | int], channel: "Channel", filter_users: QuerySet[User]
    ) -> QuerySet[Assignment]:
        return (
            Assignment.objects.select_related("address", "channel", "address__user")
            .filter(active=True, channel=channel)
            .exclude(id__in=delivered)
        ).filter(address__user_id__in=filter_users)

    def get_distributionlist_pending_subscriptions(
        self, delivered: list[str | int], channel: "Channel", filter_users: QuerySet[User]
    ) -> QuerySet[Assignment]:
        return (
            self.distribution.recipients.select_related(
                "address",
                "channel",
                "address__user",
            )
            .filter(active=True, channel=channel)
            .exclude(id__in=delivered)
        ).filter(address__user_id__in=filter_users)

    def notify_to_channel(
        self, channel: "Channel", assignment: Assignment, context: dict[str, Any]
    ) -> tuple[str | None, int | None]:
        dispatcher: "Dispatcher" = channel.dispatcher
        addr: "Address" = assignment.address
        logger.debug(f"channel: {channel} , assignment: {assignment} , context: {context}")
        if message_template := self.get_message(channel):
            logger.debug(f"message: {message_template}")
            context.update({"channel": channel, "address": addr.value})
            subject, message, html_message = message_template.render(context)
            payload: Payload = Payload(
                event=self.event,
                user=addr.user,
                subject=subject,
                message=message,
                html_message=html_message,
            )
            dispatcher.send(addr.value, payload, assignment=assignment)
            return addr.value, message_template.pk

        return None, None

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

    def get_messages(self, channel: "Channel") -> QuerySet["MessageTemplate"]:
        from .messagetemplate import MessageTemplate

        return (
            MessageTemplate.objects.filter(channel=channel)
            .filter(models.Q(event=self.event, notification=self) | models.Q(event=self.event, notification=None))
            .order_by("notification")
        )

    def get_message(self, channel: "Channel") -> "MessageTemplate | None":
        if channel not in self._cached_messages:
            ret = self.get_messages(channel).first()
            self._cached_messages[channel] = ret
        return self._cached_messages[channel]

    def create_message(
        self, name: str, channel: "Channel", defaults: dict[str, Any] | None = None
    ) -> "MessageTemplate":
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
