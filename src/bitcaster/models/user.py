import logging
from typing import TYPE_CHECKING

from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import UserManager as BaseUserManager
from django.db import models
from django.db.models import QuerySet
from django.utils.crypto import RANDOM_STRING_CHARS
from django.utils.translation import gettext_lazy as _

if TYPE_CHECKING:
    from .address import Address

logger = logging.getLogger(__name__)

TOKEN_CHARS = f"{RANDOM_STRING_CHARS}-#@^*_+~;<>,."


class UserManager(BaseUserManager["User"]):
    pass


class User(AbstractUser):
    addresses: "QuerySet[Address]"

    custom_fields = models.JSONField(default=dict, blank=True)
    objects = UserManager()

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
        app_label = "bitcaster"
        abstract = False
        permissions = (("bitcaster.lock_system", "Can lock system components"),)
