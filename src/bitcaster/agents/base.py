import abc
from typing import TYPE_CHECKING, Any, cast

from django import forms
from django.core.exceptions import ValidationError
from strategy_field.registry import Registry

if TYPE_CHECKING:
    from bitcaster.models import Monitor


class AgentMeta(type["Agent"]):
    _all = {}
    verbose_name: str = ""

    def __repr__(cls) -> str:
        return cls.verbose_name or cls.__name__

    def __new__(cls: type["Agent"], class_name: str, bases: tuple[Any], attrs: dict[str, Any]) -> "Agent":
        if attrs["__qualname__"] == "Agent":
            return super().__new__(cls, class_name, bases, attrs)
        cls = super().__new__(cls, class_name, bases, attrs)
        if cls not in agentManager and "abstract" not in attrs:  # pragma: no branch
            agentManager.register(cls)
        return cast("Agent", cls)


class AgentConfig(forms.Form):
    help_text = ""


class Agent(metaclass=AgentMeta):
    config_class: "type[AgentConfig] | None" = AgentConfig
    verbose_name = ""

    def __init__(self, monitor: "Monitor") -> None:
        self.monitor: "Monitor" = monitor

    def __repr__(self) -> str:
        return self.verbose_name or self.__class__.__name__

    @property
    def config(self) -> dict[str, Any]:
        cfg: "AgentConfig" = self.config_class(data=self.monitor.config)
        if not cfg.is_valid():
            raise ValidationError(cfg.errors)
        return cfg.cleaned_data

    @abc.abstractmethod
    def check(self, notify: bool = True, update: bool = True) -> None: ...

    @abc.abstractmethod
    def notify(self) -> None: ...

    @abc.abstractmethod
    def changes_detected(self) -> bool: ...


class AgentManager(Registry):
    pass


agentManager = AgentManager(Agent)
