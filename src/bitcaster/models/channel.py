from typing import Any, MutableMapping

from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from strategy_field.fields import StrategyField

from bitcaster.dispatchers.base import Dispatcher, dispatcherManager

from .mixins import ScopedMixin


class ChannelManager(models.Manager["Channel"]):

    def get_or_create(self, defaults: MutableMapping[str, Any] | None = None, **kwargs: Any) -> "tuple[Channel, bool]":
        if kwargs.get("application"):
            kwargs["project"] = kwargs["application"].project
            kwargs["organization"] = kwargs["application"].project.organization
        elif kwargs.get("project"):
            kwargs["organization"] = kwargs["project"].organization

        if defaults and defaults.get("application"):
            defaults["project"] = defaults["application"].project
            defaults["organization"] = defaults["application"].project.organization
        elif defaults and defaults.get("project"):
            defaults["organization"] = defaults["project"].organization

        return super().get_or_create(defaults, **kwargs)

    def update_or_create(
        self, defaults: MutableMapping[str, Any] | None = None, **kwargs: Any
    ) -> "tuple[Channel, bool]":
        if kwargs and kwargs.get("application"):
            kwargs["project"] = kwargs["application"].project
            kwargs["organization"] = kwargs["application"].project.organization
        elif kwargs.get("project"):
            kwargs["organization"] = kwargs["project"].organization

        if defaults and defaults.get("application"):
            defaults["project"] = defaults["application"].project
            defaults["organization"] = defaults["application"].project.organization
        elif defaults and defaults.get("project"):
            defaults["organization"] = defaults["project"].organization

        return super().update_or_create(defaults, **kwargs)

    def active(self) -> models.QuerySet["Channel"]:
        return self.get_queryset().filter(active=True, locked=False)


class Channel(ScopedMixin, models.Model):
    SYSTEM_EMAIL_CHANNEL_NAME = "System Email Channel"

    name = models.CharField(_("Name"), max_length=255, db_collation="case_insensitive")
    dispatcher: "Dispatcher" = StrategyField(registry=dispatcherManager, default="test")
    config = models.JSONField(blank=True, default=dict)

    active = models.BooleanField(default=True)
    locked = models.BooleanField(default=False)

    objects = ChannelManager()

    class Meta:
        unique_together = (
            ("organization", "name"),
            ("organization", "project", "name"),
            ("organization", "project", "application", "name"),
        )
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name

    @cached_property
    def from_email(self) -> str:
        if self.application:
            return self.application.from_email
        elif self.project:
            return self.project.from_email
        else:
            return str(self.organization.from_email)

    @cached_property
    def subject_prefix(self) -> str:
        if self.application:
            return str(self.application.subject_prefix)
        elif self.project:
            return self.project.subject_prefix
        else:
            return str(self.organization.subject_prefix)
