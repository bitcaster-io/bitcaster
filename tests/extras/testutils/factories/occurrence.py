from typing import Any

import factory
from django.utils import timezone

from bitcaster.models import Occurrence

from .base import AutoRegisterModelFactory
from .event import EventFactory


class OccurrenceFactory(AutoRegisterModelFactory[Occurrence]):
    timestamp = factory.Faker("date_time", tzinfo=timezone.get_current_timezone())

    class Meta:
        model = Occurrence

    event = factory.SubFactory(EventFactory)
    status = Occurrence.Status.NEW
    context: dict[str, Any] = {}
