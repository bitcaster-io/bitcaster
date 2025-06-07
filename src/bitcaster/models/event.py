from typing import TYPE_CHECKING, Any

from django.db import models
from django.utils.translation import gettext_lazy as _

from ..constants import bitcaster
from ..utils.http import absolute_reverse
from .application import Application
from .channel import Channel
from .mixins import BitcasterBaseModel, BitcasterBaselManager, LockMixin, SlugMixin
from .notification import Notification

if TYPE_CHECKING:
    from django.db.models import QuerySet

    from bitcaster.models import DistributionList, Message, Occurrence

    from .notification import NotificationManager
    from .occurrence import OccurrenceOptions


class EventManager(BitcasterBaselManager["Event"]):
    def get_by_natural_key(self, slug: str, app: str, prj: str, org: str, *args: Any) -> "Event":
        return self.get(
            application__project__organization__slug=org,
            application__project__slug=prj,
            application__slug=app,
            slug=slug,
        )

    def get_queryset(self) -> "QuerySet[Event]":
        return super().get_queryset().select_related("application__project", "application__project__organization")


class Event(SlugMixin, LockMixin, BitcasterBaseModel):
    # messages: "QuerySet[Message]"

    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name="events")
    description = models.CharField(max_length=255, blank=True, null=True)
    active = models.BooleanField(default=True)
    newsletter = models.BooleanField(default=False, help_text=_("Do not customise notifications per single user"))
    channels = models.ManyToManyField(Channel, blank=True)
    occurrence_retention = models.IntegerField(
        blank=True,
        null=True,
        help_text=_(
            "Number of days (from last update) after which related Occurrences can be purged. "
            "If not specified, system default will be used."
        ),
    )
    notifications: "NotificationManager"

    objects = EventManager()

    class Meta:
        unique_together = (
            ("name", "application"),
            ("slug", "application"),
        )
        ordering = ("name",)

    def __init__(self, *args: Any, **kwargs: Any):
        self._cached_messages: dict[Channel, Message] = {}
        super().__init__(*args, **kwargs)

    def __str__(self) -> str:
        return self.name

    def natural_key(self) -> tuple[str, ...]:
        return self.slug, *self.application.natural_key()

    def delete(self, using: str | None = None, keep_parents: bool = False) -> tuple[int, dict[str, Any]]:
        if self.application.project.organization.name == bitcaster.ORGANIZATION:
            return 0, {}
        return super().delete(using, keep_parents)

    def trigger(
        self,
        *,
        context: dict[str, Any],
        options: "OccurrenceOptions | None" = None,
        cid: Any | None = None,
        parent: "Occurrence | None" = None,
    ) -> "Occurrence":
        from .occurrence import Occurrence

        if cid:
            cid = str(cid)
        return Occurrence.objects.create(
            event=self, context=context, options=options or {}, correlation_id=cid, parent=parent
        )

    def create_message(self, name: str, channel: Channel, defaults: dict[str, Any] | None = None) -> "Message":
        return self.messages.get_or_create(
            organization=self.application.project.organization,
            name=name,
            channel=channel,
            notification=None,
            event=self,
            application=self.application,
            project=self.application.project,
            defaults=defaults if defaults else {},
        )[0]

    def create_notification(
        self, name: str, defaults: dict[str, Any] | None = None, distribution: "DistributionList | None" = None
    ) -> "Notification":
        return Notification.objects.get_or_create(
            name=name, event=self, defaults=defaults if defaults else {}, distribution=distribution
        )[0]

    def get_trigger_url(self) -> str:
        return absolute_reverse(
            "api:event-trigger",
            args=[
                self.application.project.organization.slug,
                self.application.project.slug,
                self.application.slug,
                self.slug,
            ],
        )
