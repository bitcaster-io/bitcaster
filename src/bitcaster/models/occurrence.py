import logging
from datetime import timedelta
from typing import TYPE_CHECKING, Any, NotRequired, TypedDict

from constance import config
from django.db import models
from django.db.models.expressions import F
from django.db.models.functions import Coalesce
from django.utils import timezone
from django.utils.translation import gettext as _

from ..constants import bitcaster
from .event import Event
from .mixins import BitcasterBaseModel, BitcasterBaselManager

if TYPE_CHECKING:
    from .application import Application
    from .assignment import Assignment
    from .channel import Channel
    from .message import Message
    from .notification import Notification

    OccurrenceData = TypedDict("OccurrenceData", {"delivered": list[str | int], "recipients": list[tuple[str, str]]})  # noqa: UP013

logger = logging.getLogger(__name__)


class OccurrenceOptions(TypedDict):
    limit_to: NotRequired[list[str]]
    channels: NotRequired[list[str]]
    environs: NotRequired[list[str]]


class OccurrenceManager(BitcasterBaselManager["Occurrence"]):
    def get_by_natural_key(self, timestamp: str, evt: str, app: str, prj: str, org: str) -> "Occurrence":
        return self.get(
            timestamp=timestamp,
            event__application__project__organization__slug=org,
            event__application__project__slug=prj,
            event__application__slug=app,
            event__slug=evt,
        )

    def system(self, *args: Any, **kwargs: Any) -> models.QuerySet["Occurrence"]:
        return self.filter(event__application__name=bitcaster.APPLICATION).filter(*args, **kwargs)

    def purgeable(self, *args: Any, **kwargs: Any) -> models.QuerySet["Occurrence"]:
        return self.filter(
            last_updated__lt=timezone.now()
            - models.ExpressionWrapper(  # type: ignore
                timedelta(days=1) * Coalesce(F("event__occurrence_retention"), config.OCCURRENCE_DEFAULT_RETENTION),  # type: ignore
                output_field=models.DurationField(),
            )
        ).filter(*args, **kwargs)


class Occurrence(BitcasterBaseModel):
    class Status(models.TextChoices):
        NEW = "NEW", _("New")
        PROCESSED = "PROCESSED", _("Processed")
        FAILED = "FAILED", _("Failed")

    timestamp = models.DateTimeField(auto_now_add=True, help_text=_("Timestamp when occurrence has been created."))
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    context = models.JSONField(blank=True, default=dict, help_text=_("Context provided by the sender"))
    options: "OccurrenceOptions" = models.JSONField(  # type: ignore[assignment]
        blank=True, default=dict, help_text=_("Options provided by the sender to route linked notifications")
    )
    correlation_id = models.CharField(max_length=255, editable=False, blank=True, null=True)
    recipients = models.IntegerField(default=0, help_text=_("Total number of recipients"))
    newsletter = models.BooleanField(default=False, help_text=_("Do not customise notifications per single user"))
    data: "OccurrenceData" = models.JSONField(  # type: ignore[assignment]
        default=dict, help_text=_("Information about the processing (recipients, channels)")
    )
    status = models.CharField(choices=Status, default=Status.NEW.value, max_length=20)
    attempts = models.IntegerField(default=5)
    parent = models.ForeignKey("self", editable=False, blank=True, null=True, on_delete=models.CASCADE)

    objects = OccurrenceManager()

    class Meta:
        ordering = ("timestamp",)
        constraints = [models.UniqueConstraint(fields=("timestamp", "event"), name="occurrence_unique")]

    def __str__(self) -> str:
        return f"Occurrence of {self.event.name} on {self.timestamp}"

    def natural_key(self) -> tuple[str, ...]:
        return str(self.timestamp), *self.event.natural_key()

    def __init__(self, *args: Any, **kwargs: Any):
        self._cached_messages: dict[Channel, Message] = {}
        super().__init__(*args, **kwargs)

    def get_context(self) -> dict[str, Any]:
        return self.context | {
            "timestamp": self.timestamp,
            "event": self.event,
        }

    @property
    def application(self) -> "Application":
        return self.event.application

    def process(self) -> bool:
        assignment: "Assignment"
        notification: "Notification"
        delivered = self.data.get("delivered", [])
        recipients = self.data.get("recipients", [])
        assignment_filter = {}
        notification_filter = {}
        channel_filter = {}
        if limit := self.options.get("limit_to", []):
            assignment_filter["address__value__in"] = limit

        if channels := self.options.get("channels", []):
            channel_filter["pk__in"] = channels
        if environs := self.options.get("environs", []):
            notification_filter["environments__overlap"] = environs

        for notification in self.event.notifications.filter(**notification_filter).match(self.context):
            context = notification.get_context(self.get_context())
            logger.debug(f"Processing occurrence {self.id} , context: {context}")
            for channel in self.event.channels.filter(**channel_filter):
                for assignment in notification.get_pending_subscriptions(delivered, channel).filter(
                    **assignment_filter
                ):
                    try:
                        notification.notify_to_channel(channel, assignment, context)

                        delivered.append(assignment.id)
                        recipients.append((assignment.address.value, assignment.channel.name))
                    except Exception as e:
                        logger.exception(e)
                        return False
                    finally:
                        self.data = {"delivered": delivered, "recipients": recipients}
                        self.save()
        return True
