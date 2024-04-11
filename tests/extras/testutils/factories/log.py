import factory

from bitcaster.models import LogMessage

from .base import AutoRegisterModelFactory
from .org import ApplicationFactory


class LogEntryFactory(AutoRegisterModelFactory):
    level = "INFO"
    application = factory.SubFactory(ApplicationFactory)
    message = "Message for {{ event.name }} on channel {{channel.name}}"

    class Meta:
        model = LogMessage
