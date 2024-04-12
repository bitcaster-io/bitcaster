import logging

from django.contrib.auth.models import Group
from django.db import models
from django.utils.translation import gettext as _

from .org import Organization
from .user import User

logger = logging.getLogger(__name__)


class Role(models.Model):
    name = models.CharField(verbose_name=_("Name"), max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="roles")
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
