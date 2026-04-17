import logging
from typing import TYPE_CHECKING, Any

from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from ..constants import bitcaster
from .mixins import BitcasterBaseModel, BitcasterBaselManager, LockMixin, SlugMixin
from .project import Project
from .user import User

if TYPE_CHECKING:
    from django.db.models import QuerySet
    from django.db.models.fields.related_descriptors import RelatedManager

    from bitcaster.models import Channel, Event, MessageTemplate, Organization

logger = logging.getLogger(__name__)


class ApplicationManager(BitcasterBaselManager["Application"]):
    def get_by_natural_key(self, slug: str, prj: "str", org: str) -> "Application":
        return self.get(slug=slug, project__organization__slug=org, project__slug=prj)

    def local(self, **kwargs: Any) -> "QuerySet[Application]":
        return self.exclude(project__organization__name=bitcaster.ORGANIZATION).filter(**kwargs)


class Application(SlugMixin, LockMixin, BitcasterBaseModel):
    class AutoCreateOption(models.IntegerChoices):
        PROCESS = 100, _("Create eevent and process")
        INACTIVE = 10, _("Create eevent and set it not active")
        PAUSED = 20, _("Create eevent and set it paused")
        DUMMY = 30, _("Create event but do not trigger it")

    project = models.ForeignKey(
        Project,
        verbose_name=_("Project"),
        on_delete=models.CASCADE,
        related_name="applications",
        help_text=_("project this application belong to"),
    )
    owner = models.ForeignKey(
        User,
        verbose_name=_("Owner"),
        on_delete=models.PROTECT,
        related_name="applications",
        blank=True,
        help_text=_("owner of this application"),
    )

    active = models.BooleanField(
        verbose_name=_("active"), default=True, help_text=_("Whether the application should be active")
    )
    auto_create_event = models.BooleanField(
        verbose_name=_("auto create events"),
        default=False,
        help_text=_("If true unknown events will be automatically created"),
    )
    auto_create_options = models.IntegerField(
        verbose_name=_("auto create event options"),
        choices=AutoCreateOption.choices,
        default=AutoCreateOption.PROCESS,
        help_text=_("If true unknown events will be automatically created"),
    )
    from_email = models.EmailField(
        verbose_name=_("From email"), blank=True, default="", help_text=_("default from address for emails")
    )
    subject_prefix = models.CharField(
        verbose_name=_("subject prefix"),
        max_length=50,
        default="[Bitcaster] ",
        help_text=_("Default prefix for messages supporting subject"),
    )
    advanced_configuration = models.JSONField(
        verbose_name=_("Advanced configuration"),
        blank=True,
        null=True,
        default=dict,
        help_text=_("Advanced configuration, i.e. for attachment support"),
    )

    events: "QuerySet[Event]"
    objects = ApplicationManager()

    if TYPE_CHECKING:
        messagetemplate_set: RelatedManager[MessageTemplate]

    class Meta:
        ordering = ("name",)
        unique_together = (("project", "name"), ("project", "slug"))
        verbose_name = _("Application")
        verbose_name_plural = _("Applications")

    def can_be_locked(self) -> bool:
        return self.project.organization.name != bitcaster.ORGANIZATION

    def natural_key(self) -> tuple[str, str, str]:
        return self.slug, *self.project.natural_key()

    @cached_property
    def organization(self) -> "Organization":
        return self.project.organization

    def save(self, *args: Any, **kwargs: Any) -> None:
        try:
            _ = self.owner
        except User.DoesNotExist:
            self.owner = self.project.owner
        super().save(*args, **kwargs)

    def register_event(self, name: str, description: str = "") -> "Event":
        ev: "Event" = self.events.get_or_create(name=name, defaults={"description": description, "active": False})[0]
        return ev

    def create_message(
        self, name: str, channel: "Channel", defaults: dict[str, Any] | None = None
    ) -> "MessageTemplate":
        return self.messagetemplate_set.get_or_create(
            name=name,
            channel=channel,
            notification=None,
            event=None,
            application=self,
            project=self.project,
            organization=self.project.organization,
            defaults=defaults if defaults else {},
        )[0]
