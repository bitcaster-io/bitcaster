import logging

import factory
from django.utils import timezone

from bitcaster.models import UserMessage

from .base import AutoRegisterModelFactory
from .event import EventFactory
from .user import UserFactory


class UserMessageFactory(AutoRegisterModelFactory[UserMessage]):
    class Meta:
        model = UserMessage

    user = factory.SubFactory(UserFactory)
    event = factory.SubFactory(EventFactory)
    level = logging.DEBUG
    subject = factory.Sequence(lambda x: f"Subject #{x}")
    message = factory.Sequence(lambda x: f"Message #{x}")
    created = factory.LazyFunction(timezone.now)
    displayed = False
    read = None
