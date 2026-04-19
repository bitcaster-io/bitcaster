from typing import TYPE_CHECKING, Any, Iterable

from django.db import models
from django.db.models import Q
from django.db.models.base import ModelBase
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from smart_selects.db_fields import ChainedForeignKey
from strategy_field.fields import StrategyField

from bitcaster.dispatchers.base import Dispatcher, MessageProtocol, dispatcherManager

from .mixins import BitcasterBaseModel, LockMixin, ScopedManager

if TYPE_CHECKING:
    from bitcaster.models import Application, Organization, Project


class ChannelManager(ScopedManager["Channel"]):
    def active(self) -> models.QuerySet["Channel"]:
        return self.get_queryset().filter(active=True, locked=False)

    def get_by_natural_key(self, name: str, prj: str, org: str) -> "Channel":
        filters: dict[str, str | None] = {}
        if prj:
            filters["project__slug"] = prj
        else:
            filters["project"] = None

        return self.get(name=name, organization__slug=org, **filters)


class Channel(LockMixin, BitcasterBaseModel):
    organization = models.ForeignKey(
        "Organization",
        verbose_name=_("Organization"),
        on_delete=models.CASCADE,
        related_name="%(class)s_set",
        blank=True,
        help_text=_("Chanel organization"),
    )
    project = ChainedForeignKey(
        "Project",
        blank=True,
        null=True,
        chained_field="organization",
        chained_model_field="organization",
        show_all=False,
        help_text=_("project linked to this channel"),
    )
    name = models.CharField(verbose_name=_("Name"), max_length=255, help_text=_("channel name"))
    dispatcher: "Dispatcher" = StrategyField(
        verbose_name=_("Dispatcher"), registry=dispatcherManager, default="test", help_text=_("channel dispatcher")
    )
    config = models.JSONField(
        verbose_name=_("configuration"), blank=True, default=dict, help_text=_("Channel configuration")
    )
    protocol = models.CharField(
        verbose_name=_("protocol"), max_length=50, choices=MessageProtocol.choices, help_text=_("channel protocol")
    )
    active = models.BooleanField(verbose_name=_("active"), default=True, help_text=_("enable/disable channel"))
    parent = ChainedForeignKey(
        "self",
        blank=True,
        null=True,
        chained_field="organization",
        chained_model_field="organization",
        show_all=False,
        help_text=_("parent channel"),
    )
    objects = ChannelManager()

    class Meta:
        verbose_name = _("Channel")
        verbose_name_plural = _("Channels")
        ordering = ("name",)
        constraints = [
            models.UniqueConstraint(
                name="%(app_label)s_%(class)s_org_name",
                fields=("organization", "name"),
                condition=Q(project__isnull=True),
            ),
            models.UniqueConstraint(
                name="%(app_label)s_%(class)s_org_project_app_name",
                fields=("organization", "project", "name"),
            ),
        ]

    def __str__(self) -> str:
        return self.name

    def can_be_locked(self) -> bool:
        return True

    def save(
        self,
        *args: Any,
        force_insert: bool | tuple[ModelBase, ...] = False,
        force_update: bool = False,
        using: str | None = None,
        update_fields: Iterable[str] | None = None,
    ) -> None:
        self.protocol = self.dispatcher.protocol
        super().save(force_insert, force_update, using, update_fields)

    @property
    def owner(self) -> "Application | Project | Organization":
        if self.project:
            return self.project
        return self.organization

    def natural_key(self) -> tuple[str | None, ...]:
        if self.project:
            return self.name, *self.project.natural_key()
        return self.name, None, *self.organization.natural_key()

    @cached_property
    def from_email(self) -> str:
        if self.project:
            return self.project.from_email
        return str(self.organization.from_email)

    @cached_property
    def subject_prefix(self) -> str:
        if self.project:
            return self.project.subject_prefix
        return str(self.organization.subject_prefix)
