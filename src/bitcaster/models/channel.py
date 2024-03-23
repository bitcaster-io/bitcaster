from django.db import models
from strategy_field.fields import StrategyField

from bitcaster.dispatchers.base import dispatcherManager

from .auth import Organisation


class Channel(models.Model):
    organization = models.ForeignKey(Organisation, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, db_collation="case_insensitive")
    dispatcher = StrategyField(registry=dispatcherManager)
