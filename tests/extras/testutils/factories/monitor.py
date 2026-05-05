import factory
from factory import Sequence

from testutils.agent import XAgent

from strategy_field.utils import fqn

from bitcaster.models import Monitor

from .base import AutoRegisterModelFactory
from .event import EventFactory

__all__ = [
    "MonitorFactory",
]


class MonitorFactory(AutoRegisterModelFactory[Monitor]):
    name = Sequence(lambda n: "Monitor-%03d" % n)
    event = factory.SubFactory(EventFactory)
    agent = fqn(XAgent)
    config = {"foo": "bar"}

    class Meta:
        model = Monitor
