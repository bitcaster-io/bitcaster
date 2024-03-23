from django.contrib.auth.models import AbstractUser, Group
from django.db import models
from django.utils.translation import gettext_lazy as _
from treebeard.mp_tree import MP_Node


class Sender(MP_Node):
    name = models.CharField(max_length=255, db_collation="case_insensitive")
    node_order_by = ['name']

    def __str__(self) -> str:
        return str(self.name)


class OrganisationManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(depth=1)


class Organisation(Sender):
    objects = OrganisationManager()

    class Meta:
        proxy = True


class ApplicationManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(depth=2)


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
