import factory

from bitcaster.models import LogEntry

from .base import AutoRegisterModelFactory
from .org import ApplicationFactory


class LogEntryFactory(AutoRegisterModelFactory):
    level = "INFO"
    application = factory.SubFactory(ApplicationFactory)
    message = "Message for {{ event.name }} on channel {{channel.name}}"

    class Meta:
        model = LogEntry
