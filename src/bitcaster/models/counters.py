from django.db import models
from django.db.models import F
from strategy_field.utils import fqn


def get_id(event):
    return '{0}-{1.pk}'.format(fqn(event), event)


class CounterManager(models.Manager):
    def initialize(self, target):
        self.get_or_create(target=get_id(target))

    def increment(self, target):
        self.filter(target=get_id(target)).update(total=F('total') + 1)


class Counter(models.Model):

    target = models.CharField(unique=True,
                              max_length=200)
    total = models.IntegerField(default=0)
    errors = models.IntegerField(default=0)

    objects = CounterManager()
