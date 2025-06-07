import logging
from typing import TYPE_CHECKING, Any

from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils.translation import gettext as _

from ..constants import bitcaster
from .mixins import BitcasterBaseModel, BitcasterBaselManager, LockMixin, SlugMixin
from .organization import Organization
from .user import User

if TYPE_CHECKING:
    from django.db.models import QuerySet

    from bitcaster.models import Message

    from .channel import Channel

logger = logging.getLogger(__name__)


class ProjectManager(BitcasterBaselManager["Project"]):
    def get_by_natural_key(self, slug: str, org: str) -> "Project":
        return self.get(slug=slug, organization__slug=org)

    def local(self, **kwargs: Any) -> "QuerySet[Project]":
        return self.exclude(organization__name=bitcaster.ORGANIZATION).filter(**kwargs)


class Project(SlugMixin, LockMixin, BitcasterBaseModel):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="projects")
    owner = models.ForeignKey(User, verbose_name=_("Owner"), on_delete=models.PROTECT, blank=True)
    from_email = models.EmailField(blank=True, default="", help_text=_("default from address for emails"))
    subject_prefix = models.CharField(
        verbose_name=_("Subject Prefix"),
        max_length=50,
        default="[Bitcaster] ",
        help_text=_("Default prefix for messages supporting subject"),
    )
    environments = ArrayField(
        models.CharField(max_length=20, blank=True, null=True),
        blank=True,
        null=True,
        help_text=_("Environments available for project"),
    )
    objects = ProjectManager()

    class Meta:
        verbose_name = _("Project")
        verbose_name_plural = _("Projects")
        ordering = ("name",)
        unique_together = (
            ("organization", "name"),
            ("organization", "slug"),
        )

    def natural_key(self) -> tuple[str, str]:
        return self.slug, *self.organization.natural_key()

    def save(self, *args: Any, **kwargs: Any) -> None:
        try:
            _ = self.owner
        except User.DoesNotExist:
            self.owner = self.organization.owner
        super().save(*args, **kwargs)

    def create_message(self, name: str, channel: "Channel", defaults: dict[str, Any] | None = None) -> "Message":
        return self.message_set.get_or_create(
            name=name,
            channel=channel,
            notification=None,
            event=None,
            application=None,
            project=self,
            organization=self.organization,
            defaults=defaults if defaults else {},
        )[0]
