from typing import TYPE_CHECKING, Any

from django.db import models
from django.utils.translation import gettext_lazy as _

from .assignment import Assignment
from .mixins import BitcasterBaseModel, BitcasterBaselManager

if TYPE_CHECKING:
    from .user import User


class SubscriptionManager(BitcasterBaselManager["Subscription"]):
    def get_by_natural_key(self, pk: str, *args: Any) -> "Subscription":
        return self.get(pk=pk)


class Subscription(BitcasterBaseModel):
    """A user's direct subscription to a Notification.

    Allows a user to listen to a Notification without being member of any
    DistributionList. The user is derived from the subscribed Assignment's address.
    """

    notification = models.ForeignKey(
        "bitcaster.Notification",
        verbose_name=_("Notification"),
        on_delete=models.CASCADE,
        related_name="subscriptions",
        help_text=_("Notification the user wants to listen to"),
    )
    assignment = models.ForeignKey(
        Assignment,
        verbose_name=_("Assignment"),
        on_delete=models.CASCADE,
        related_name="subscriptions",
        help_text=_("Assignment used to receive the notification"),
    )
    active = models.BooleanField(verbose_name=_("Active"), default=True, help_text=_("If the subscription is active"))

    objects = SubscriptionManager()

    class Meta:
        verbose_name = _("Subscription")
        verbose_name_plural = _("Subscriptions")
        constraints = [
            models.UniqueConstraint(
                fields=("notification", "assignment"),
                name="%(app_label)s_%(class)s_notification_assignment",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.assignment} - {self.notification}"

    def natural_key(self) -> tuple[str]:
        return (str(self.pk),)

    @property
    def user(self) -> "User":
        return self.assignment.address.user
