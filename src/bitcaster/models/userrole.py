import logging

from django.contrib.auth.models import Group
from django.db import models

from .organization import Organization
from .user import User

logger = logging.getLogger(__name__)


class UserRole(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="roles")
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
