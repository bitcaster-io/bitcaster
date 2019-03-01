import abc
import logging

from rest_framework.fields import empty
from strategy_field.utils import fqn

from bitcaster import get_full_version
from bitcaster.api.fields import EventField
from bitcaster.configurable import ConfigurableMixin
from bitcaster.utils.language import classproperty

from . import serializers

logger = logging.getLogger(__name__)


class AgentOptions(serializers.Serializer):
    event = EventField(choices=())

    def __init__(self, instance=None, data=empty, **kwargs):
        super().__init__(instance, data, **kwargs)


class Agent(ConfigurableMixin, metaclass=abc.ABCMeta):
    options_class = AgentOptions
    icon = 'agent.png'
    __core__ = True
    __version__ = get_full_version()

    def get_options_form(self, **kwargs):
        application = kwargs.pop('application', None)
        if not kwargs['data']:
            kwargs['data'] = empty
        form = super().get_options_form(**kwargs)
        if application:
            form.fields['event'].choices = application.events.values_list('id', 'name')
        return form

    @classproperty
    def fqn(cls):
        return fqn(cls)

    def poll(self):
        pass

    def notify(self):
        pass
