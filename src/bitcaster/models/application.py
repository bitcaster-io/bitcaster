import logging
from typing import TYPE_CHECKING, Any, Optional

from django.db import models
from django.db.models import QuerySet
from django.utils.functional import cached_property
from django.utils.translation import gettext as _

from .mixins import BitcasterBaselManager, BitcasterBaseModel, LockMixin, SlugMixin
from .project import Project
from .user import User

if TYPE_CHECKING:
    from bitcaster.models import Channel, Event, Message, Organization

logger = logging.getLogger(__name__)


class ApplicationManager(BitcasterBaselManager["Application"]):

    def get_by_natural_key(self, slug: str, prj: "str", org: str) -> "Application":
        return self.get(slug=slug, project__organization__slug=org, project__slug=prj)


class Application(SlugMixin, LockMixin, BitcasterBaseModel):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="applications")
    owner = models.ForeignKey(User, verbose_name=_("Owner"), on_delete=models.PROTECT, blank=True)

    active = models.BooleanField(default=True, help_text=_("Whether the application should be active"))

    from_email = models.EmailField(blank=True, default="", help_text=_("default from address for emails"))
    subject_prefix = models.CharField(
        max_length=50,
        default="[Bitcaster] ",
        help_text=_("Default prefix for messages supporting subject"),
    )

    events: "QuerySet[Event]"
    objects = ApplicationManager()

    class Meta:
        ordering = ("name",)
        unique_together = (("project", "name"), ("project", "slug"))

    def natural_key(self) -> tuple[str | None, ...]:
        return self.slug, *self.project.natural_key()

    @cached_property
    def organization(self) -> "Organization":
        return self.project.organization

    def save(self, *args: Any, **kwargs: Any) -> None:
        try:
            self.owner
        except User.DoesNotExist:
            self.owner = self.project.owner
        super().save(*args, **kwargs)

    def register_event(self, name: str, description: str = "") -> "Event":
        from bitcaster.models import Event

        ev: "Event" = self.events.get_or_create(name=name, description=description, active=False)[0]
        return ev

    def create_message(self, name: str, channel: "Channel", defaults: Optional[dict[str, Any]] = None) -> "Message":
        return self.message_set.get_or_create(
            name=name,
            channel=channel,
            notification=None,
            event=None,
            application=self,
            project=self.project,
            organization=self.project.organization,
            defaults=defaults if defaults else {},
        )[0]
