import factory
from factory import Sequence
from strategy_field.utils import fqn
from testutils.agent import XAgent

from bitcaster.models import Monitor

from . import PeriodicTaskFactory
from .base import AutoRegisterModelFactory
from .event import EventFactory

__all__ = ["MonitorFactory", "PeriodicTaskFactory"]


class MonitorFactory(AutoRegisterModelFactory[Monitor]):
    name = Sequence(lambda n: "Monitor-%03d" % n)
    event = factory.SubFactory(EventFactory)
    agent = fqn(XAgent)
    schedule = factory.SubFactory(PeriodicTaskFactory)
    config = {"foo": "bar"}

    class Meta:
        model = Monitor
