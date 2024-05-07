import logging
from typing import TYPE_CHECKING, Any, Optional

from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils.translation import gettext as _

from .channel import Channel
from .mixins import SlugMixin
from .organization import Organization
from .user import User

if TYPE_CHECKING:
    from bitcaster.models import Message


logger = logging.getLogger(__name__)


class Project(SlugMixin, models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="projects")
    owner = models.ForeignKey(User, verbose_name=_("Owner"), on_delete=models.PROTECT, blank=True)
    locked = models.BooleanField(default=False, help_text=_("Security lock of project"))
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

    class Meta:
        ordering = ("name",)
        unique_together = (("organization", "name"),)

    def save(self, *args: Any, **kwargs: Any) -> None:
        try:
            self.owner
        except User.DoesNotExist:
            self.owner = self.organization.owner
        super().save(*args, **kwargs)

    def create_message(self, name: str, channel: "Channel", defaults: Optional[dict[str, Any]] = None) -> "Message":
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
