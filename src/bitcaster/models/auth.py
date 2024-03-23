import logging
from typing import List

from django.contrib.auth.models import AbstractUser, Group
from django.db import models
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from treebeard.mp_tree import MP_Node

logger = logging.getLogger(__name__)


class Sender(MP_Node):
    name = models.CharField(max_length=255, db_collation="case_insensitive")
    node_order_by: List[str] = ["name"]

    def __str__(self) -> str:
        return str(self.name)


class OrganisationManager(models.Manager["Organisation"]):
    def get_queryset(self) -> "QuerySet[Organisation]":
        return super().get_queryset().filter(depth=1)


class ProjectManager(models.Manager["Project"]):
    def get_queryset(self) -> "QuerySet[Project]":
        return super().get_queryset().filter(depth=2)


class ApplicationManager(models.Manager["Application"]):
    def get_queryset(self) -> "QuerySet[Application]":
        return super().get_queryset().filter(depth=3)


class SectionManager(models.Manager["Section"]):
    def get_queryset(self) -> "QuerySet[Section]":
        return super().get_queryset().filter(depth__lt=3)


class Project(Sender):
    objects = ProjectManager()

    class Meta:
        proxy = True


class Organisation(Sender):
    objects = OrganisationManager()

    class Meta:
        proxy = True


class Section(Sender):
    objects = SectionManager()

    class Meta:
        proxy = True


class Application(Sender):
    objects = ApplicationManager()

    class Meta:
        proxy = True


class User(AbstractUser):
    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
        app_label = "bitcaster"
        abstract = False


class Role(models.Model):
    name = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    sender = models.ForeignKey(Sender, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
