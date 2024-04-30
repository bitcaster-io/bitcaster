import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from bitcaster import models
from bitcaster.state import state

logger = logging.getLogger(__name__)


@receiver(post_save, sender=models.Application)
@receiver(post_save, sender=models.Project)
@receiver(post_save, sender=models.ApiKey)
@receiver(post_save, sender=models.Organization)
def save_last_choices(sender, instance, **kwargs):
    if getattr(instance, "organization", None):
        state.add_cookie("organization", instance.organization.pk)
    if getattr(instance, "project", None):
        state.add_cookie("project", instance.project.pk)
    if getattr(instance, "application", None):
        state.add_cookie("application", instance.application.pk)
