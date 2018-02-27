# -*- coding: utf-8 -*-
from django.db import models
from django.db.models import F
from strategy_field.utils import fqn


class CounterManager(models.Manager):
    def initialize(self, target):
        t = "{0}-{1.pk}".format(fqn(target), target)
        self.get_or_create(target=t)

    def increment(self, target):
        t = "{0}-{1.pk}".format(fqn(target), target)
        self.filter(target=t).update(total=F('total') + 1)


class Counter(models.Model):
    target = models.CharField(unique=True,
                              max_length=200)
    total = models.IntegerField(default=0)
    errors = models.IntegerField(default=0)

    objects = CounterManager()


class Occurence(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    event = models.ForeignKey('mercury.Event',
                              on_delete=models.CASCADE)
    submissions = models.IntegerField(default=0,
                                      help_text="number of subscriptions")
    successes = models.IntegerField(default=0)
    failures = models.IntegerField(default=0)


class LogEntry(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    application = models.ForeignKey('mercury.Application',
                                    related_name='+',
                                    on_delete=models.CASCADE)
    event = models.ForeignKey('mercury.Event',
                              related_name='+',
                              on_delete=models.CASCADE)
    subscription = models.ForeignKey('mercury.Application',
                                     null=True,
                                     related_name='+',
                                     on_delete=models.SET_NULL)
    channel = models.ForeignKey('mercury.Channel',
                                null=True,
                                related_name='+',
                                on_delete=models.SET_NULL)
