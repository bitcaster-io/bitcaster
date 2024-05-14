from typing import TYPE_CHECKING, Iterable, Optional

from django.db import models
from django.db.models import Q
from django.db.models.base import ModelBase
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from strategy_field.fields import StrategyField

from bitcaster.dispatchers.base import Dispatcher, MessageProtocol, dispatcherManager

from .mixins import BitcasterBaseModel, LockMixin, ScopedManager, ScopedMixin

if TYPE_CHECKING:
    from bitcaster.models import Application, Organization, Project


class ChannelManager(ScopedManager["Channel"]):
    def active(self) -> models.QuerySet["Channel"]:
        return self.get_queryset().filter(active=True, locked=False)

    def get_by_natural_key(self, name: str, app: str, prj: str, org: str) -> "Channel":
        filters: dict[str, str | None] = {}
        if app:
            filters["application__slug"] = app
        else:
            filters["application"] = None

        if prj:
            filters["project__slug"] = prj
        else:
            filters["project"] = None

        return self.get(name=name, organization__slug=org, **filters)


class Channel(ScopedMixin, LockMixin, BitcasterBaseModel):
    application: "Application"

    name = models.CharField(_("Name"), max_length=255)
    dispatcher: "Dispatcher" = StrategyField(registry=dispatcherManager, default="test")
    config = models.JSONField(blank=True, default=dict)
    protocol = models.CharField(choices=MessageProtocol.choices)
    active = models.BooleanField(default=True)

    objects = ChannelManager()

    class Meta:
        unique_together = (
            ("organization", "name"),
            ("organization", "project", "name"),
            ("organization", "project", "application", "name"),
        )
        ordering = ("name",)
        constraints = [
            models.UniqueConstraint(
                name="%(app_label)s_%(class)s_org_name",
                fields=("organization", "name"),
                condition=Q(project__isnull=True, application__isnull=True),
            ),
            models.UniqueConstraint(
                name="%(app_label)s_%(class)s_org_project_name",
                fields=("organization", "project", "name"),
                condition=Q(application__isnull=True),
            ),
            models.UniqueConstraint(
                name="%(app_label)s_%(class)s_org_project_app_name",
                fields=("organization", "project", "application", "name"),
            ),
        ]

    def __str__(self) -> str:
        return self.name

    def save(
        self,
        force_insert: bool | tuple[ModelBase, ...] = False,
        force_update: bool = False,
        using: Optional[str] = None,
        update_fields: Optional[Iterable[str]] = None,
    ) -> None:
        self.protocol = self.dispatcher.protocol
        super().save(force_insert, force_update, using, update_fields)

    @property
    def owner(self) -> "Application | Project | Organization":
        if self.application:
            return self.application
        elif self.project:
            return self.project
        else:
            return self.organization

    def natural_key(self) -> tuple[str | None, ...]:
        if self.application:
            return self.name, *self.application.natural_key()
        elif self.project:
            return self.name, None, *self.project.natural_key()
        else:
            return self.name, None, None, *self.organization.natural_key()

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
