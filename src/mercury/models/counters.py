# -*- coding: utf-8 -*-
from django.db import models
from django.db.models import F

from mercury.models import Event


class CounterManager(models.Manager):
    def increment(self, target):
        self.filter(target=target).update(total=F('total') + 1)


class Counter(models.Model):
    target = models.CharField(unique=True,
                              max_length=200)
    total = models.IntegerField(default=0)
    errors = models.IntegerField(default=0)

    objects = CounterManager()


class Occurence(models.Model):
    event = models.ForeignKey(Event,
                              on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_created=True)
    submissions = models.IntegerField(default=0,
                                      help_text="number of subscriptions")
    successes = models.IntegerField(default=0)
    failures = models.IntegerField(default=0)
