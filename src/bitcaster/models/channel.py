from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from strategy_field.fields import StrategyField

from bitcaster.dispatchers.base import Dispatcher, dispatcherManager

from .org import Application, Organization


class ChannelManager(models.Manager["Channel"]):
    def active(self) -> models.QuerySet["Channel"]:
        return self.get_queryset().filter(active=True, locked=False)

    def for_application(self, app: "Application") -> models.QuerySet["Channel"]:
        return self.get_queryset().filter(organization=app.project.organization, application=app)


class Channel(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, blank=True, null=True)
    application = models.ForeignKey(Application, on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=255, db_collation="case_insensitive")
    dispatcher: "Dispatcher" = StrategyField(registry=dispatcherManager, default="test")
    config = models.JSONField(blank=True, default=dict)

    active = models.BooleanField(default=True)
    locked = models.BooleanField(default=False)

    objects = ChannelManager()

    def __str__(self) -> str:
        return self.name

    def clean(self) -> None:
        if not self.dispatcher:
            self.dispatcher = dispatcherManager.get_default()
        if not self.organization and self.application:
            self.organization = self.application.organization
        if not self.application and not self.organization:
            raise ValidationError(_("Channel must have an application or an organization"))
