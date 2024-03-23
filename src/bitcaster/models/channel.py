from django.db import models
from strategy_field.fields import StrategyField
from .auth import Organisation
from bitcaster.dispatchers.base import dispatcherManager


class Channel(models.Model):
    organization = models.ForeignKey(Organisation, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, db_collation="case_insensitive")
    dispatcher = StrategyField(registry=dispatcherManager)
