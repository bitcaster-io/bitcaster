from logging import getLogger

from strategy_field.registry import Registry as Registry

logger = getLogger(__name__)

agent_registry = Registry('bitcaster.agents.base.Agent')
