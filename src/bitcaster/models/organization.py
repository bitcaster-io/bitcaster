import logging
from typing import TYPE_CHECKING, Any

from django.db import models
from django.db.models import QuerySet
from django.utils.translation import gettext as _

from ..constants import bitcaster
from .mixins import BitcasterBaseModel, BitcasterBaselManager, SlugMixin
from .user import User

if TYPE_CHECKING:
    from bitcaster.models import Channel, Message

logger = logging.getLogger(__name__)


class OrganizationManager(BitcasterBaselManager["Organization"]):
    def get_by_natural_key(self, slug: str) -> "Organization":
        return self.get(slug=slug)

    def local(self, **kwargs: Any) -> "QuerySet[Organization]":
        return self.exclude(name=bitcaster.ORGANIZATION).filter(**kwargs)


class Organization(SlugMixin, BitcasterBaseModel):
    from_email = models.EmailField(blank=True, default="", help_text=_("default from address for emails"))
    subject_prefix = models.CharField(
        verbose_name=_("Subject Prefix"),
        max_length=50,
        default="[Bitcaster] ",
        help_text=_("Default prefix for messages supporting subject"),
    )
    owner = models.ForeignKey(
        User, verbose_name=_("Owner"), on_delete=models.PROTECT, related_name="managed_organizations"
    )

    objects = OrganizationManager()

    class Meta:
        verbose_name = _("Organization")
        verbose_name_plural = _("Organizations")
        ordering = ("name",)
        constraints = [
            models.UniqueConstraint(fields=("slug",), name="org_slug_unique"),
            models.UniqueConstraint(fields=("slug", "owner"), name="owner_slug_unique"),
        ]

    @property
    def users(self) -> QuerySet["User"]:
        return User.objects.filter(roles__organization=self)

    def natural_key(self) -> tuple[str]:
        return (self.slug,)

    def create_message(self, name: str, channel: "Channel", defaults: "dict[str, Any] | None" = None) -> "Message":
        return self.message_set.get_or_create(
            name=name,
            channel=channel,
            notification=None,
            event=None,
            application=None,
            project=None,
            organization=self,
            defaults=defaults if defaults else {},
        )[0]
