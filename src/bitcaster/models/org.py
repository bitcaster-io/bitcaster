import logging
from typing import TYPE_CHECKING, Any

from django.db import models
from django.db.models import QuerySet
from django.utils.translation import gettext as _

from .mixins import SlugMixin
from .user import User

if TYPE_CHECKING:
    from bitcaster.models import Event

logger = logging.getLogger(__name__)


class Organization(SlugMixin, models.Model):
    from_email = models.EmailField(blank=True, default="", help_text=_("default from address for emails"))
    subject_prefix = models.CharField(
        verbose_name=_("Subject Prefix"),
        max_length=50,
        default="[Bitcaster] ",
        help_text=_("Default prefix for messages supporting subject"),
    )
    owner = models.ForeignKey(User, verbose_name=_("Owner"), on_delete=models.PROTECT)

    class Meta:
        ordering = ("name",)


class Project(SlugMixin, models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="projects")
    owner = models.ForeignKey(User, verbose_name=_("Owner"), on_delete=models.PROTECT, blank=True)
    locked = models.BooleanField(default=False, help_text=_("Security lock of project"))

    class Meta:
        ordering = ("name",)

    def save(self, *args: Any, **kwargs: Any) -> None:
        try:
            self.owner
        except User.DoesNotExist:
            self.owner = self.organization.owner
        super().save(*args, **kwargs)


class Application(SlugMixin, models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="applications")
    owner = models.ForeignKey(User, verbose_name=_("Owner"), on_delete=models.PROTECT, blank=True)

    active = models.BooleanField(default=True, help_text=_("Whether the application should be active"))
    locked = models.BooleanField(default=False, help_text=_("Security lock of applications"))

    from_email = models.EmailField(blank=True, default="", help_text=_("default from address for emails"))
    subject_prefix = models.CharField(
        max_length=50,
        default="[Bitcaster] ",
        help_text=_("Default prefix for messages supporting subject"),
    )

    events: "QuerySet[Event]"

    class Meta:
        ordering = ("name",)

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
