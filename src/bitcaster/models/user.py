import logging
from typing import TYPE_CHECKING

from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import UserManager as BaseUserManager
from django.db import models
from django.utils.crypto import RANDOM_STRING_CHARS
from django.utils.translation import gettext_lazy as _

from .mixins import BitcasterBaseModel

if TYPE_CHECKING:
    from bitcaster.dispatchers.base import MessageProtocol
    from bitcaster.models import Address

logger = logging.getLogger(__name__)

TOKEN_CHARS = f"{RANDOM_STRING_CHARS}-#@^*_+~;<>,."


class UserManager(BaseUserManager["User"]):

    def get_by_natural_key(self, username: str | None) -> "User":
        return self.get(username=username)


class User(BitcasterBaseModel, AbstractUser):
    custom_fields = models.JSONField(default=dict, blank=True)
    objects = UserManager()

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
        app_label = "bitcaster"
        abstract = False
        permissions = (("bitcaster.lock_system", "Can lock system components"),)

    def natural_key(self) -> tuple[str]:
        return (self.username,)

    def get_address_for_protocol(self, protocol: "MessageProtocol") -> "Address | None":
        return self.addresses.filter_for_protocol(protocol).first()
