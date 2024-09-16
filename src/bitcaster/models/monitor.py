from django.db import models
from strategy_field.fields import StrategyField

from bitcaster.agents.base import Agent, agentManager


class Monitor(models.Model):
    name = models.CharField(max_length=255)
    agent: "Agent" = StrategyField(registry=agentManager, default="test")
    config = models.JSONField(blank=True, default=dict)
    data = models.JSONField(blank=True, default=dict)
