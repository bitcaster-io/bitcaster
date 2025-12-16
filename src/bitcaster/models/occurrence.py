import logging
from datetime import timedelta
from typing import TYPE_CHECKING, Any, NotRequired, TypedDict

from constance import config
from django.db import models, transaction
from django.db.models.expressions import F
from django.db.models.functions import Coalesce
from django.utils import timezone
from django.utils.translation import gettext as _

from ..constants import SystemEvent, bitcaster
from .event import Event
from .mixins import BitcasterBaseModel, BitcasterBaselManager

if TYPE_CHECKING:
    from ..types.filtering import QuerysetFilter
    from .application import Application
    from .assignment import Assignment
    from .channel import Channel
    from .message import Message
    from .notification import Notification

    OccurrenceData = TypedDict("OccurrenceData", {"delivered": list[str | int], "recipients": list[tuple[str, str]]})  # noqa: UP013

    class OccurrenceOptions(TypedDict):
        limit_to: NotRequired[list[str]]
        channels: NotRequired[list[str]]
        environs: NotRequired[list[str]]
        filters: NotRequired[QuerysetFilter]


logger = logging.getLogger(__name__)


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
            - models.ExpressionWrapper(
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
    recipients = models.IntegerField(default=0, help_text=_("Total number of reached recipients"))
    newsletter = models.BooleanField(default=False, help_text=_("Do not customise notifications per single user"))
    data: "OccurrenceData" = models.JSONField(  # type: ignore[assignment]
        default=dict, help_text=_("Information about the processing (recipients, channels)")
    )
    status = models.CharField(
        choices=Status, default=Status.NEW.value, max_length=20, help_text=_("Status of the occurrence")
    )
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

    def process(self) -> int:
        from bitcaster.models import Occurrence

        num_sent = 0
        try:
            with transaction.atomic():
                o: Occurrence = Occurrence.objects.select_related("event").select_for_update().get(id=self.pk)
                if o.attempts > 0:
                    o.attempts = o.attempts - 1
                    o.save()
                    if o.status == Occurrence.Status.NEW:
                        success, ret = o._process()
                        delivered = len(ret["delivered"])
                        o.data = ret
                        if success:
                            o.status = Occurrence.Status.PROCESSED
                        o.recipients = delivered
                        if delivered == 0 and o.event.name != SystemEvent.OCCURRENCE_SILENCE.value:
                            bitcaster.trigger_event(
                                SystemEvent.OCCURRENCE_SILENCE,
                                o.context,
                                options=o.options,
                                correlation_id=o.correlation_id,
                                parent=o,
                            )
                        num_sent = o.recipients
                        o.save()
                elif (
                    o.attempts == 0
                    and o.status == Occurrence.Status.NEW
                    and o.event.name != SystemEvent.OCCURRENCE_SILENCE.value
                ):
                    o.status = Occurrence.Status.FAILED
                    bitcaster.trigger_event(
                        SystemEvent.OCCURRENCE_ERROR, options=o.options, correlation_id=o.correlation_id, parent=o
                    )
                    num_sent = 0
                    o.save()
        except Exception as e:
            logger.exception(e)
        return num_sent

    def _process(self) -> "tuple[bool, OccurrenceData]":
        assignment: "Assignment"
        notification: "Notification"
        delivered = self.data.get("delivered", [])
        recipients = self.data.get("recipients", [])
        assignment_filter = {}
        notification_filter = {}
        channel_filter = {}
        success = True
        if limit := self.options.get("limit_to", []):
            assignment_filter["address__value__in"] = limit
        api_filtering = self.options.get("filters", {}) or {}

        if channels := self.options.get("channels", []):
            channel_filter["pk__in"] = channels
        if environs := self.options.get("environs", []):
            notification_filter["environments__overlap"] = environs

        try:
            for notification in self.event.notifications.filter(**notification_filter).match(self.context):
                context = notification.get_context(self.get_context())
                logger.debug(f"Processing occurrence {self.id} , context: {context}")

                for channel in self.event.channels.filter(**channel_filter):
                    for assignment in notification.get_pending_subscriptions(delivered, channel, api_filtering).filter(
                        **assignment_filter
                    ):
                        notification.notify_to_channel(channel, assignment, context)
                        delivered.append(assignment.id)
                        recipients.append((assignment.address.value, assignment.channel.name))
        except Exception as e:
            logger.exception(e)
            success = False
        finally:
            data: "OccurrenceData" = {"delivered": delivered, "recipients": recipients}
        return success, data
