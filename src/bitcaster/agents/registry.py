# -*- coding: utf-8 -*-
from strategy_field.registry import Registry as Registry

from bitcaster.logging import getLogger

logger = getLogger(__name__)

agent_registry = Registry('bitcaster.agents.base.Agent')
