import enum
import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, cast

from constance import config
from django.db import models
from django.utils.functional import cached_property

if TYPE_CHECKING:
    from bitcaster.models import Application, Event, Group, Occurrence, Organization, User
    from bitcaster.models.occurrence import OccurrenceOptions

logger = logging.getLogger(__name__)


class CacheKey:
    DASHBOARDS_EVENTS: str = "dashboard_events"


@dataclass
class Bitcaster:
    ORGANIZATION = "OS4D"
    PROJECT = "BITCASTER-IO"
    APPLICATION = "Bitcaster"
    SYSTEM_USER = "__SYSTEM__"
    _app: "Application | None" = None
    _local_org: "Organization | None" = None

    @staticmethod
    def initialize(admin: "User") -> "Application":
        from bitcaster.models import Application, DistributionList, Group, Organization, Project

        os4d = Organization.objects.get_or_create(name=bitcaster.ORGANIZATION, defaults={"owner": admin})[0]
        prj = Project.objects.get_or_create(name=bitcaster.PROJECT, organization=os4d, owner=os4d.owner)[0]
        app = Application.objects.get_or_create(name=bitcaster.APPLICATION, project=prj, owner=os4d.owner)[0]
        Group.objects.get_or_create(name=config.NEW_USER_DEFAULT_GROUP)

        for event_name in SystemEvent:
            app.register_event(event_name.value)

        DistributionList.objects.get_or_create(name=DistributionList.ADMINS, project=prj)
        bitcaster._app = None
        return app

    @property
    def system_user(self) -> "User":
        from bitcaster.models import User

        return User.objects.get_or_create(username=self.SYSTEM_USER)[0]

    @cached_property
    def system_user_id(self) -> int:
        return self.system_user.pk

    @property
    def local_organization(self) -> "Organization":
        from bitcaster.models import Organization

        if not self._local_org:
            self._local_org = Organization.objects.exclude(name=self.ORGANIZATION).get()
        return self._local_org

    @property
    def app(self) -> "Application":
        from bitcaster.models import Application

        if not self._app:
            self._app = Application.objects.select_related("project", "project__organization").get(
                name=self.APPLICATION, project__name=self.PROJECT, project__organization__name=self.ORGANIZATION
            )
        return self._app

    def trigger_event(
        self,
        evt: "SystemEvent",
        context: dict[str, Any] | None = None,
        *,
        options: "OccurrenceOptions | None" = None,
        correlation_id: Any | None = None,
        parent: "Occurrence | None" = None,
    ) -> "Occurrence":
        e: "Event" = self.app.events.get(name=evt.value)
        return e.trigger(context=(context or {}), options=options or {}, cid=correlation_id, parent=parent)

    def get_default_group(self) -> "Group":
        from bitcaster.models.group import Group

        return cast("Group", Group.objects.get_or_create(name=config.NEW_USER_DEFAULT_GROUP)[0])


class AddressType(models.TextChoices):
    GENERIC = "GENERIC", "Generic address"
    EMAIL = "email", "Email"
    PHONE = "phone", "Phone"
    ACCOUNT = "account", "Account"


class SystemEvent(enum.Enum):
    CHANNEL_LOCKED = "channel_locked"
    APPLICATION_LOCKED = "application_locked"
    APPLICATION_UNLOCKED = "application_unlocked"
    OCCURRENCE_SILENCE = "silent_occurrence"
    OCCURRENCE_ERROR = "error_occurrence"


bitcaster = Bitcaster()
