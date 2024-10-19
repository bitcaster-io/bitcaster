import logging
from typing import Any

from django.core.cache import cache
from django.db.models.signals import post_save
from django.dispatch import receiver

from bitcaster.constants import CacheKey
from bitcaster.models import Occurrence

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Occurrence, dispatch_uid="invalidate_occurrence_cache")
def invalidate_occurrence_cache(**kwargs: Any) -> None:
    cache.delete(CacheKey.DASHBOARDS_EVENTS)
