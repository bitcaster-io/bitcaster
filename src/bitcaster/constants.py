import enum
from typing import TYPE_CHECKING

from django.db import models

if TYPE_CHECKING:
    from bitcaster.models import Application, User


class Bitcaster:
    ORGANIZATION = "OS4D"
    PROJECT = "BITCASTER"
    APPLICATION = "Bitcaster"

    @staticmethod
    def initialize(admin: "User") -> "Application":
        from bitcaster.models import Application, Organization, Project

        os4d = Organization.objects.get_or_create(name=Bitcaster.ORGANIZATION, owner=admin)[0]
        prj = Project.objects.get_or_create(name=Bitcaster.PROJECT, organization=os4d, owner=os4d.owner)[0]
        app = Application.objects.get_or_create(name=Bitcaster.APPLICATION, project=prj, owner=os4d.owner)[0]

        for event_name in SystemEvent:
            app.register_event(event_name.value)

        return app


class AddressType(models.TextChoices):
    GENERIC = "GENERIC", "Generic address"
    EMAIL = "email", "Email"
    PHONE = "phone", "Phone"
    ACCOUNT = "account", "Account"


class SystemEvent(enum.Enum):
    APPLICATION_LOCKED = "application_locked"
    APPLICATION_UNLOCKED = "application_unlocked"
    OCCURRENCE_SILENCE = "silent_occurrence"
    OCCURRENCE_ERROR = "error_occurrence"
