import logging
from typing import Any

from django.conf import settings
from django.contrib.auth import user_logged_in
from django.db.models.signals import post_save
from django.dispatch import receiver

from bitcaster import models
from bitcaster.constants import AddressType
from bitcaster.dispatchers import UserMessageDispatcher
from bitcaster.models import Address, Assignment, Channel, Organization, Project
from bitcaster.state import state

logger = logging.getLogger(__name__)


@receiver(post_save, sender=models.Application)
@receiver(post_save, sender=models.Project)
@receiver(post_save, sender=models.ApiKey)
@receiver(post_save, sender=models.Organization)
def save_last_choices(sender: Any, instance: Any, **kwargs: Any) -> None:
    if getattr(instance, "organization", None):
        state.add_cookie("organization", instance.organization.pk)
    if getattr(instance, "project", None):
        state.add_cookie("project", instance.project.pk)
    if getattr(instance, "application", None):
        state.add_cookie("application", instance.application.pk)


@receiver(user_logged_in, sender=models.User)
def on_login(sender: Any, user: models.User, **kwargs: Any) -> None:
    if not state.get_cookie("organization") and (org := Organization.objects.local().first()):
        state.add_cookie("organization", org.pk)
    if not state.get_cookie("project") and (prj := Project.objects.local().first()):
        state.add_cookie("project", prj.pk)


@receiver(post_save, sender=models.User)
def auto_set_superusers(sender: Any, instance: models.User, created: bool = False, **kwargs: Any) -> None:
    if created and instance.email in settings.SUPERUSERS:
        instance.is_superuser = True
        instance.is_staff = True
        instance.save()


@receiver(post_save, sender=models.User)
def auto_assign_to_messages(sender: Any, instance: models.User, created: bool = False, **kwargs: Any) -> None:
    if created and instance.email:
        for channel in Channel.objects.filter(dispatcher=UserMessageDispatcher):
            address, __ = Address.objects.get_or_create(
                user=instance, value=instance.email, defaults={"name": "Email", "type": AddressType.EMAIL}
            )
            Assignment.objects.get_or_create(
                channel=channel, address=address, validated=True, defaults={"active": True}
            )
