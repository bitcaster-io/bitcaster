import abc

from bitcaster import get_full_version
from bitcaster.configurable import ConfigurableMixin

from . import serializers


class AgentOptions(serializers.Serializer):
    pass


class Agent(ConfigurableMixin, metaclass=abc.ABCMeta):
    options_class = AgentOptions
    icon = 'agent.png'
    __core__ = True
    __version__ = get_full_version()

    def poll(self):
        pass

    def notify(self):
        pass
