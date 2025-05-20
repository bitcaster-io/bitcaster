import logging
from typing import Any

from django.contrib.auth import user_logged_in
from django.db.models.signals import post_save
from django.dispatch import receiver

from bitcaster import models
from bitcaster.models import Organization, Project
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
    if not state.get_cookie("organization"):  # pragma: no branch
        if org := Organization.objects.local().first():
            state.add_cookie("organization", org.pk)
    if not state.get_cookie("project"):  # pragma: no branch
        if prj := Project.objects.local().first():
            state.add_cookie("project", prj.pk)
