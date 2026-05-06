import factory

from django.contrib.admin.models import LogEntry as DjangoLogEntry

from bitcaster.models import LogEntry

from .base import AutoRegisterModelFactory
from .contenttypes import ContentTypeFactory
from .user import UserFactory


class LogEntryFactory(AutoRegisterModelFactory[LogEntry]):
    action_flag = LogEntry.ADDITION
    user = factory.SubFactory(UserFactory)
    content_type = factory.SubFactory(ContentTypeFactory)

    class Meta:
        model = LogEntry


class DjangoLogEntryFactory(AutoRegisterModelFactory[DjangoLogEntry]):
    action_flag = LogEntry.ADDITION
    user = factory.SubFactory(UserFactory)
    content_type = factory.SubFactory(ContentTypeFactory)

    class Meta:
        model = DjangoLogEntry
