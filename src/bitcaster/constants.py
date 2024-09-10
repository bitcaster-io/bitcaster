import enum
import logging
from typing import TYPE_CHECKING, Any, Optional, cast

from constance import config
from django.db import models

from bitcaster.utils.language import class_property

if TYPE_CHECKING:
    from bitcaster.models import Application, Event, Group, Occurrence, User
    from bitcaster.models.occurrence import OccurrenceOptions

logger = logging.getLogger(__name__)


class CacheKey:
    DASHBOARDS_EVENTS = "dashboard_events"


class Bitcaster:
    ORGANIZATION = "OS4D"
    PROJECT = "BITCASTER"
    APPLICATION = "Bitcaster"
    _app: "Optional[Application]" = None

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
        Bitcaster._app = None
        return app

    @class_property
    def app(cls) -> "Application":
        from bitcaster.models import Application

        if not cls._app:
            cls._app = Application.objects.select_related("project", "project__organization").get(
                name=cls.APPLICATION, project__name=cls.PROJECT, project__organization__name=cls.ORGANIZATION
            )
        return cls._app

    @classmethod
    def trigger_event(
        cls,
        evt: "SystemEvent",
        context: Optional[dict[str, Any]] = None,
        *,
        options: "Optional[OccurrenceOptions]" = None,
        correlation_id: Optional[Any] = None,
        parent: "Optional[Occurrence]" = None,
    ) -> "Occurrence":
        e: "Event" = cls.app.events.get(name=evt.value)
        return e.trigger(context=(context or {}), options=options or {}, cid=correlation_id, parent=parent)

    @classmethod
    def get_default_group(cls) -> "Group":
        from bitcaster.models.group import Group

        return cast(Group, Group.objects.get(name=config.NEW_USER_DEFAULT_GROUP))


class AddressType(models.TextChoices):
    GENERIC = "GENERIC", "Generic address"
    EMAIL = "email", "Email"
    PHONE = "phone", "Phone"
    ACCOUNT = "account", "Account"


class SystemEvent(enum.Enum):
    CHANNEL_LOCKED = "application_locked"
    APPLICATION_LOCKED = "application_locked"
    APPLICATION_UNLOCKED = "application_unlocked"
    OCCURRENCE_SILENCE = "silent_occurrence"
    OCCURRENCE_ERROR = "error_occurrence"
