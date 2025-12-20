import logging
from typing import Any

from django.db.models.signals import post_save
from django.dispatch import receiver

from bitcaster.models import Occurrence

from .manager import CacheManager

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Occurrence, dispatch_uid="invalidate_occurrence_cache")
def invalidate_occurrence_cache(instance: "Occurrence", **kwargs: Any) -> None:
    cm = CacheManager(None)
    cm.incr_version(f"inspect:{instance.pk}")
