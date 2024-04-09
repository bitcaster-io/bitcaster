import logging
from typing import TYPE_CHECKING, Any

from django.db import models
from django.db.models import QuerySet
from django.utils.text import slugify

if TYPE_CHECKING:
    from bitcaster.models import Event

logger = logging.getLogger(__name__)


class Organization(models.Model):
    name = models.CharField(max_length=255, db_collation="case_insensitive", unique=True)

    def __str__(self) -> str:
        return self.name


class Project(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, db_collation="case_insensitive", unique=True)

    def __str__(self) -> str:
        return self.name


class Application(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, db_collation="case_insensitive", unique=True)
    active = models.BooleanField(default=True)

    event_types: "QuerySet[Event]"

    def __str__(self) -> str:
        return self.name

    def register_event(self, name: str, description: str = "", active: bool = True) -> "Event":
        from bitcaster.models import Event

        ev: "Event" = self.event_types.get_or_create(name=name, description=description, active=active)[0]
        return ev

    def save(self, *args: Any, **kwargs: Any) -> None:
        self.name = slugify(self.name)
        super().save(*args, **kwargs)
