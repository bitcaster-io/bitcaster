import logging
from typing import TYPE_CHECKING, Any, Optional

from django.db import models
from django.utils.translation import gettext as _

from .mixins import SlugMixin
from .user import User

if TYPE_CHECKING:
    from bitcaster.models import Channel, Message

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

    def create_message(self, name: str, channel: "Channel", defaults: "Optional[dict[str, Any]]" = None) -> "Message":
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
