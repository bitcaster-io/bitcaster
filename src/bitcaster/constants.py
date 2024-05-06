import enum
import functools
import logging
from typing import TYPE_CHECKING, Any, Optional

from django.db import models

if TYPE_CHECKING:
    from bitcaster.models import Application, Occurrence, User
    from bitcaster.models.occurrence import OccurrenceOptions

logger = logging.getLogger(__name__)


class Bitcaster:
    ORGANIZATION = "OS4D"
    PROJECT = "BITCASTER"
    APPLICATION = "Bitcaster"

    @staticmethod
    def initialize(admin: "User") -> "Application":
        from bitcaster.models import (
            Application,
            DistributionList,
            Organization,
            Project,
        )

        os4d = Organization.objects.get_or_create(name=Bitcaster.ORGANIZATION, owner=admin)[0]
        prj = Project.objects.get_or_create(name=Bitcaster.PROJECT, organization=os4d, owner=os4d.owner)[0]
        app = Application.objects.get_or_create(name=Bitcaster.APPLICATION, project=prj, owner=os4d.owner)[0]

        for event_name in SystemEvent:
            app.register_event(event_name.value)

        DistributionList.objects.get_or_create(name=DistributionList.ADMINS, project=prj)
        return app

    @classmethod
    @property
    @functools.cache
    def app(cls) -> "Application":
        from bitcaster.models import Application

        return Application.objects.get(
            name=cls.APPLICATION, project__name=cls.PROJECT, project__organization__name=cls.ORGANIZATION
        )

    @classmethod
    def trigger_event(
        cls,
        evt: "SystemEvent",
        context: Optional[dict[str, Any]] = None,
        *,
        options: "Optional[OccurrenceOptions]" = None,
        correlation_id: Optional[Any] = None,
    ) -> "Optional[Occurrence]":
        return cls.app.events.get(name=evt.value).trigger(context or {}, options=options or {}, cid=correlation_id)


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
