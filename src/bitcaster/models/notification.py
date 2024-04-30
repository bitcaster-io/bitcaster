from typing import TYPE_CHECKING, Any, Optional

import jmespath
import yaml
from django.db import models
from django.db.models import QuerySet

from .distribution import DistributionList
from .validation import Validation

if TYPE_CHECKING:
    from bitcaster.types.core import YamlPayload

    from .channel import Channel


class NotificationQuerySet(models.QuerySet["Subscription"]):

    def match(self, payload: dict[str, Any], rules: "Optional[YamlPayload]" = None) -> list["Notification"]:
        for subscription in self.all():
            if subscription.match_filter(payload, rules=rules):
                yield subscription


class Notification(models.Model):
    event = models.ForeignKey("bitcaster.Event", on_delete=models.CASCADE, related_name="notifications")
    distribution = models.ForeignKey(
        DistributionList, blank=True, null=True, on_delete=models.CASCADE, related_name="notifications"
    )

    payload_filter = models.TextField(blank=True, null=True)
    extra_context = models.JSONField(default=dict)
    objects = NotificationQuerySet.as_manager()

    def get_context(self, ctx: dict[str, str]) -> dict[str, Any]:
        return {"event": self.event, **ctx}

    def get_pending_subscriptions(self, delivered: list[str], channel: "Channel") -> QuerySet[Validation]:
        return (
            self.distribution.recipients.select_related(
                "address",
                "channel",
                "address__user",
            )
            .filter(active=True, channel=channel)
            .exclude(id__in=delivered)
        )

    @classmethod
    def match_filter_impl(cls, filter_rules_dict: "YamlPayload", payload: "YamlPayload") -> bool:
        if not filter_rules_dict:
            return True

        if isinstance(filter_rules_dict, str):
            # this is a leaf, apply the filter
            return bool(jmespath.search(filter_rules_dict, payload))

        # it is not a str hence it must be a dict with one of AND, OR, NOT
        if and_stm := filter_rules_dict.get("AND"):
            return all([cls.match_filter_impl(rules, payload) for rules in and_stm])
        elif or_stm := filter_rules_dict.get("OR"):
            return any([cls.match_filter_impl(rules, payload) for rules in or_stm])
        elif not_stm := filter_rules_dict.get("NOT"):
            return not cls.match_filter_impl(not_stm, payload)
        return False

    def match_filter(self, payload: "YamlPayload", rules: Optional[dict[str, Any] | str] = None) -> bool:
        """Check if given payload matches rules.

        If no rules are specified, it defaults to match rules configured in subscription.
        """
        if not rules:
            rules = yaml.safe_load(self.payload_filter or "")
        return self.match_filter_impl(rules, payload)

    @staticmethod
    def check_filter(filter_rules_dict: "YamlPayload"):
        return jmespath.compile(filter_rules_dict)
