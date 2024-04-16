from typing import Any, MutableMapping

from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from strategy_field.fields import StrategyField

from bitcaster.dispatchers.base import Dispatcher, dispatcherManager

from .org import Application, Organization, Project


class ChannelManager(models.Manager["Channel"]):

    def get_or_create(self, defaults: MutableMapping[str, Any] | None = None, **kwargs: Any) -> "tuple[Channel, bool]":
        targets = [kwargs]
        if defaults:
            targets.append(defaults)
        for target in targets:
            if "application" in target:
                target["project"] = target["application"].project
                target["organization"] = target["application"].project.organization
            elif "project" in target:
                target["organization"] = target["project"].organization

        return super().get_or_create(defaults, **kwargs)

    def active(self) -> models.QuerySet["Channel"]:
        return self.get_queryset().filter(active=True, locked=False)

    def for_application(self, app: "Application") -> models.QuerySet["Channel"]:
        return self.get_queryset().filter(organization=app.project.organization, application=app)


class Channel(models.Model):
    SYSTEM_EMAIL_CHANNEL_NAME = "System Email Channel"

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, blank=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, blank=True, null=True)
    application = models.ForeignKey(Application, on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(_("Name"), max_length=255, db_collation="case_insensitive")
    dispatcher: "Dispatcher" = StrategyField(registry=dispatcherManager, default="test")
    config = models.JSONField(blank=True, default=dict)

    active = models.BooleanField(default=True)
    locked = models.BooleanField(default=False)

    objects = ChannelManager()

    class Meta:
        permissions = (("bitcaster.lock_channels", "Can lock channels"),)
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
        else:
            return str(self.organization.from_email)

    @cached_property
    def subject_prefix(self) -> str:
        if self.application:
            return str(self.application.subject_prefix)
        else:
            return str(self.organization.subject_prefix)

    def clean(self) -> None:
        if not self.dispatcher:
            self.dispatcher = dispatcherManager.get_default()
        try:
            if self.application:
                self.project = self.application.project
        except ObjectDoesNotExist:
            pass
        try:
            if self.project:
                self.organization = self.project.organization
        except ObjectDoesNotExist:
            pass

        # if not self.application and not self.organization:
        #     raise ValidationError(_("Channel must have an application or an organization"))
