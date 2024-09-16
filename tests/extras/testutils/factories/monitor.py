from factory import Sequence
from strategy_field.utils import fqn
from testutils.agent import XAgent
from testutils.factories.base import AutoRegisterModelFactory

from bitcaster.models import Monitor


class MonitorFactory(AutoRegisterModelFactory[Monitor]):
    name = Sequence(lambda n: "Monitor-%03d" % n)
    agent = fqn(XAgent)
