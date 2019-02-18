# -*- coding: utf-8 -*-
from strategy_field.registry import Registry as Registry

from bitcaster.logging import getLogger

logger = getLogger(__name__)

monitor_registry = Registry('bitcaster.monitor.base.Agent')
