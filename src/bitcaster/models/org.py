import logging
from typing import TYPE_CHECKING

from django.db import models
from django.db.models import QuerySet

from .mixins import SlugMixin

if TYPE_CHECKING:
    from bitcaster.models import Event

logger = logging.getLogger(__name__)


class Organization(SlugMixin, models.Model):
    from_email = models.EmailField(blank=True, default="")
    subject_prefix = models.CharField(max_length=50, default="[Bitcaster] ")


class Project(SlugMixin, models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)


class Application(SlugMixin, models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    active = models.BooleanField(default=True)
    from_email = models.EmailField(blank=True, default="")
    subject_prefix = models.CharField(max_length=50, default="[Bitcaster] ")

    events: "QuerySet[Event]"

    def register_event(self, name: str, description: str = "", active: bool = True) -> "Event":
        from bitcaster.models import Event

        ev: "Event" = self.events.get_or_create(name=name, description=description, active=active)[0]
        return ev
