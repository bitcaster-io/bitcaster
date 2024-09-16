import abc
from typing import TYPE_CHECKING, Any, cast

from django import forms
from django.core.exceptions import ValidationError
from strategy_field.registry import Registry

if TYPE_CHECKING:
    from bitcaster.models import Event, Monitor


class AgentMeta(type["Agent"]):
    _all = {}
    # _dispatchers = []
    verbose_name: str = ""

    def __repr__(cls) -> str:
        return cls.verbose_name

    def __new__(mcs: type["Agent"], class_name: str, bases: tuple[Any], attrs: dict[str, Any]) -> "Agent":
        if attrs["__qualname__"] == "Agent":
            return super().__new__(mcs, class_name, bases, attrs)
        cls = super().__new__(mcs, class_name, bases, attrs)
        if cls not in agentManager:  # pragma: no branch
            agentManager.register(cls)
        return cast(Agent, cls)


class AgentConfig(forms.Form):
    help_text = ""
    event = forms.ModelChoiceField(queryset=None)

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.fields["event"].queryset = Event.objects.all()


class Agent(metaclass=AgentMeta):
    config_class: "type[AgentConfig] | None" = AgentConfig

    def __init__(self, monitor: "Monitor") -> None:
        self.monitor = monitor

    def __repr__(cls) -> str:
        return cls.__name__

    @property
    def config(self) -> dict[str, Any]:
        cfg: "AgentConfig" = self.config_class(data=self.monitor.config)
        if not cfg.is_valid():
            raise ValidationError(cfg.errors)
        return cfg.cleaned_data

    @abc.abstractmethod
    def check(self) -> None: ...

    @abc.abstractmethod
    def notify(self) -> None: ...


class AgentManager(Registry):
    pass


agentManager = AgentManager(Agent)
