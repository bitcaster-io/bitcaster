from typing import TYPE_CHECKING, Any, NotRequired, TypedDict

import logging
from collections.abc import Generator
from datetime import timedelta

from constance import config

from django.core.exceptions import ObjectDoesNotExist
from django.db import models, transaction
from django.db.models.expressions import F
from django.db.models.functions import Coalesce
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from bitcaster.constants import SystemEvent, bitcaster

from . import LogEntry
from .event import Event
from .mixins import BitcasterBaseModel, BitcasterBaselManager

if TYPE_CHECKING:
    from django.db.models import QuerySet

    from .application import Application
    from .assignment import Assignment
    from .channel import Channel
    from .messagetemplate import MessageTemplate
    from .notification import Notification
    from ..types.filtering import QuerysetFilter

    class RenderedData(TypedDict):
        assignment_pk: int
        notification_pk: int
        notification_name: str
        channel_pk: int
        channel_name: str
        address: str
        subject: str
        message: str
        html_message: str

    class MissingTemplateData(TypedDict):
        address: str
        channel_name: str
        assignment_pk: int
        channel_pk: int
        notification_pk: int
        notification_name: str

    class OccurrenceData(TypedDict):
        delivered: list[str | int]
        recipients: list[
            tuple[str, str, int, int, int | None, int | None]
        ]  # assignment.address.value, channel.name, assignment.pk, channel.pk, notification.pk, message_template_pk
        errors: list[str]
        notifications: list[int]
        channels: list[int]
        messages: list[int]
        rendered: NotRequired[list[RenderedData]]
        missing_template: NotRequired[list[MissingTemplateData]]

    class RecipientsData(TypedDict):
        recipients: list[tuple[Assignment, Channel, Notification, MessageTemplate | None]]
        notifications: set[Notification]
        channels: set[Channel]
        messages: set[MessageTemplate]
        errors: list[str]

    class OccurrenceOptions(TypedDict):
        limit_to: NotRequired[list[str]]
        channels: NotRequired[list[str | int]]
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
                timedelta(days=1) * Coalesce(F("event__occurrence_retention"), config.OCCURRENCE_DEFAULT_RETENTION),  # type: ignore[operator]
                output_field=models.DurationField(),
            )
        ).filter(*args, **kwargs)


class Occurrence(BitcasterBaseModel):
    class Status(models.TextChoices):
        PROCESSED = "PROCESSED", _("Processed")
        FAILED = "FAILED", _("Failed")
        NEW = "NEW", _("New")

    timestamp = models.DateTimeField(
        verbose_name=_("date"), auto_now_add=True, help_text=_("Timestamp when occurrence has been created.")
    )
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    context = models.JSONField(
        verbose_name=_("context"), blank=True, default=dict, help_text=_("Context provided by the sender")
    )
    options: "OccurrenceOptions" = models.JSONField(  # type: ignore[assignment]
        verbose_name=_("Options"),
        blank=True,
        default=dict,
        help_text=_("Options provided by the sender to route linked notifications"),
    )
    correlation_id = models.CharField(
        verbose_name=_("Correlation ID"),
        max_length=255,
        blank=True,
        null=True,
        editable=False,
        help_text=_("Correlation ID provided by the sender"),
    )
    recipients = models.IntegerField(
        verbose_name=_("recipients"), default=0, help_text=_("Total number of reached recipients")
    )
    newsletter = models.BooleanField(
        verbose_name=_("newsletter mode"), default=False, help_text=_("Do not customise notifications per single user")
    )
    data: "OccurrenceData" = models.JSONField(  # type: ignore[assignment]
        verbose_name=_("Data"), default=dict, help_text=_("Information about the processing (recipients, channels)")
    )
    status = models.CharField(
        verbose_name=_("status"),
        max_length=20,
        choices=Status,
        default=Status.NEW.value,
        help_text=_("Status of the occurrence"),
    )
    attempts = models.IntegerField(
        verbose_name=_("attempts"),
        default=5,
        help_text=_("The remaining number of attempts before the occurrence is marked as failed"),
    )
    parent = models.ForeignKey("self", on_delete=models.CASCADE, blank=True, null=True, editable=False)

    objects = OccurrenceManager()

    class Meta:
        verbose_name = _("Occurrence")
        verbose_name_plural = _("Occurrences")
        ordering = ("timestamp",)
        constraints = [models.UniqueConstraint(fields=("timestamp", "event"), name="occurrence_unique")]

    def __str__(self) -> str:
        return f"{self.event.name} on {self.timestamp.strftime('%Y-%m-%d %H:%M')}"

    def natural_key(self) -> tuple[str, ...]:
        return str(self.timestamp), *self.event.natural_key()

    def __init__(self, *args: Any, **kwargs: Any):
        self._cached_messages: dict[Channel, MessageTemplate] = {}
        super().__init__(*args, **kwargs)

    def get_context(self) -> dict[str, Any]:
        return self.context | {
            "occurrence": self,
            "timestamp": self.timestamp,
            "event": self.event,
        }

    @property
    def application(self) -> "Application":
        return self.event.application

    def log_action(self) -> None:
        LogEntry.objects.log_actions(bitcaster.system_user.pk, [self], LogEntry.OTHER, "Start processing")

    def process(self) -> int:
        from bitcaster.models import Occurrence

        num_sent = 0
        try:
            with transaction.atomic():
                transaction.on_commit(self.log_action)
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

    def _get_valid_notifications(self) -> Generator["Notification", None, None]:
        notification_filter: dict[str, Any] = {"active": True}
        if environs := self.options.get("environs", []):
            notification_filter["environments__overlap"] = environs
        return self.event.notifications.filter(**notification_filter).match(self.context)

    def _get_valid_channels(self) -> "QuerySet[Channel]":
        channel_filter: dict[str, Any] = {"active": True, "locked": False, "paused": False}
        if channels := self.options.get("channels", []):
            channel_filter["pk__in"] = channels
        return self.event.channels.filter(**channel_filter)

    def collect_recipients(self) -> "RecipientsData":
        assignment: "Assignment"
        notification: "Notification"
        assignment_filter = {}
        data: "RecipientsData" = {
            "recipients": [],
            "notifications": set(),
            "channels": set(),
            "messages": set(),
            "errors": [],
        }
        if limit := self.options.get("limit_to", []):
            assignment_filter["address__value__in"] = limit
        api_filtering = self.options.get("filters", {}) or {}
        try:
            for notification in self._get_valid_notifications():
                data["notifications"].add(notification)
                context = notification.get_context(self.get_context())
                logger.debug(f"Processing occurrence {self.id} , context: {context}")
                for channel in self._get_valid_channels():
                    data["channels"].add(channel)
                    for assignment in notification.get_pending_subscriptions(
                        [], channel, api_filtering, context
                    ).filter(**assignment_filter):
                        message_template = notification.get_message(channel)
                        data["recipients"].append(
                            (
                                assignment,
                                channel,
                                notification,
                                message_template,
                            )
                        )
        except ObjectDoesNotExist as e:
            logger.exception(e)
            data["errors"].append(str(e))
        return data

    def _process(self) -> "tuple[bool, OccurrenceData]":
        assignment: "Assignment"
        notification: "Notification"
        recipients = self.data.get("recipients", [])
        notifications = set(self.data.get("notifications", []))
        channels = set(self.data.get("channels", []))
        messages = set(self.data.get("messages", []))

        recipients_data: "RecipientsData" = self.collect_recipients()
        delivered = self.data.get("delivered", [])
        errors = self.data.get("errors", [])
        success = True
        data: "OccurrenceData" = {
            "delivered": delivered,
            "recipients": [],
            "errors": errors,
            "notifications": [],
            "channels": [],
            "messages": [],
        }
        try:
            for assignment, channel, notification, message_template in recipients_data["recipients"]:
                notifications.add(notification.pk)
                channels.add(channel.pk)
                if assignment.pk not in delivered:
                    context = notification.get_context(self.get_context())
                    notification.notify_to_channel(channel, assignment, context)
                    if message_template is not None:
                        messages.add(message_template.pk)
                    delivered.append(assignment.id)
                    recipients.append(
                        (
                            assignment.address.value,
                            channel.name,
                            assignment.pk,
                            channel.pk,
                            notification.pk,
                            message_template.pk if message_template else None,
                        )
                    )
        except Exception as e:
            logger.exception(e)
            errors.append(f"{e.__class__.__name__}: {str(e)}")
            success = False
        finally:
            data["delivered"] = delivered
            data["recipients"] = recipients
            data["notifications"] = list(set(notifications))
            data["messages"] = list(set(messages))
            data["channels"] = list(set(channels))
        return success, data

    def preview(self, mode: str, limit: int | None = None) -> "tuple[bool, OccurrenceData]":
        """Dry-run of the recipient pipeline with zero side effects.

        Runs `collect_recipients` and, for `full`/`partial` modes, renders the
        message templates without dispatching anything. No Occurrence row is
        saved: the instance timestamp is set explicitly because `auto_now_add`
        only fires on `save()`.
        """
        self.timestamp = timezone.now()
        recipients_data: "RecipientsData" = self.collect_recipients()
        errors = list(recipients_data["errors"])
        data: "OccurrenceData" = {
            "delivered": [],
            "recipients": [
                (
                    assignment.address.value,
                    channel.name,
                    assignment.pk,
                    channel.pk,
                    notification.pk,
                    message_template.pk if message_template else None,
                )
                for assignment, channel, notification, message_template in recipients_data["recipients"]
            ],
            "errors": errors,
            "notifications": [n.pk for n in recipients_data["notifications"]],
            "channels": [c.pk for c in recipients_data["channels"]],
            "messages": [m.pk for m in recipients_data["messages"]],
        }
        rendered: "list[RenderedData]" = []
        missing_template: "list[MissingTemplateData]" = []
        if mode in ("full", "partial"):
            for idx, (assignment, channel, notification, message_template) in enumerate(recipients_data["recipients"]):
                if message_template is None:
                    missing_template.append(
                        {
                            "address": assignment.address.value,
                            "channel_name": channel.name,
                            "assignment_pk": assignment.pk,
                            "channel_pk": channel.pk,
                            "notification_pk": notification.pk,
                            "notification_name": notification.name,
                        }
                    )
                    continue
                if mode == "partial" and limit is not None and idx >= limit:
                    break
                try:
                    context = dict(notification.get_context(self.get_context()))
                    context.update({"channel": channel, "address": assignment.address.value, "assignment": assignment})
                    subject, message, html_message = message_template.render(context)
                    rendered.append(
                        {
                            "assignment_pk": assignment.pk,
                            "notification_pk": notification.pk,
                            "notification_name": notification.name,
                            "channel_pk": channel.pk,
                            "channel_name": channel.name,
                            "address": assignment.address.value,
                            "subject": subject,
                            "message": message,
                            "html_message": html_message,
                        }
                    )
                except Exception as e:
                    logger.exception(e)
                    errors.append(f"{e.__class__.__name__}: {str(e)}")
            data["rendered"] = rendered
            data["missing_template"] = missing_template
        return True, data
