from typing import TYPE_CHECKING, Any, Optional

from django.db import models
from django.http import HttpRequest
from django.urls import reverse
from django.utils.translation import gettext as _

from .application import Application
from .channel import Channel
from .mixins import BitcasterBaselManager, BitcasterBaseModel, LockMixin, SlugMixin
from .notification import Notification

if TYPE_CHECKING:
    from bitcaster.models import DistributionList, Message, Occurrence

    from .occurrence import OccurrenceOptions


class EventManager(BitcasterBaselManager["Event"]):
    def get_by_natural_key(self, slug: str, app: str, prj: str, org: str, *args: Any) -> "Event":
        return self.get(
            application__project__organization__slug=org,
            application__project__slug=prj,
            application__slug=app,
            slug=slug,
        )


class Event(SlugMixin, LockMixin, BitcasterBaseModel):
    # messages: "QuerySet[Message]"

    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name="events")
    description = models.CharField(max_length=255, blank=True, null=True)
    active = models.BooleanField(default=True)
    newsletter = models.BooleanField(default=False, help_text=_("Do not customise notifications per single user"))
    channels = models.ManyToManyField(Channel, blank=True)

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

    def natural_key(self) -> tuple[str, ...]:
        return self.slug, *self.application.natural_key()

    def trigger(
        self,
        context: dict[str, Any],
        *,
        options: "Optional[OccurrenceOptions]" = None,
        cid: Optional[Any] = None,
        parent: "Optional[Occurrence]" = None,
    ) -> "Occurrence":
        from .occurrence import Occurrence

        if cid:
            cid = str(cid)
        return Occurrence.objects.create(
            event=self, context=context, options=options or {}, correlation_id=cid, parent=parent
        )

    def create_message(self, name: str, channel: Channel, defaults: Optional[dict[str, Any]] = None) -> "Message":
        return self.messages.get_or_create(
            name=name,
            channel=channel,
            notification=None,
            event=self,
            application=self.application,
            project=self.application.project,
            organization=self.application.project.organization,
            defaults=defaults if defaults else {},
        )[0]

    def create_notification(
        self, name: str, defaults: Optional[dict[str, Any]] = None, distribution: "Optional[DistributionList]" = None
    ) -> "Notification":
        return Notification.objects.get_or_create(
            name=name, event=self, defaults=defaults if defaults else {}, distribution=distribution
        )[0]

    def get_trigger_url(self, request: "HttpRequest") -> str:
        url = reverse(
            "api:event-trigger",
            args=[
                self.application.project.organization.slug,
                self.application.project.slug,
                self.application.slug,
                self.slug,
            ],
        )
        return request.build_absolute_uri(url)
