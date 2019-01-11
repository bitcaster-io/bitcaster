# -*- coding: utf-8 -*-
from django.db import models
from django.db.models import F
from strategy_field.utils import fqn

from bitcaster.models.user import User


class CounterManager(models.Manager):
    def initialize(self, target):
        t = '{0}-{1.pk}'.format(fqn(target), target)
        self.get_or_create(target=t)

    def increment(self, target):
        t = '{0}-{1.pk}'.format(fqn(target), target)
        self.filter(target=t).update(total=F('total') + 1)


class Counter(models.Model):
    target = models.CharField(unique=True,
                              max_length=200)
    total = models.IntegerField(default=0)
    errors = models.IntegerField(default=0)

    objects = CounterManager()


class Occurence(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    organization = models.ForeignKey('bitcaster.Organization',
                                     on_delete=models.CASCADE)
    application = models.ForeignKey('bitcaster.Application',
                                    on_delete=models.CASCADE)
    event = models.ForeignKey('bitcaster.Event',
                              on_delete=models.CASCADE)
    origin = models.GenericIPAddressField(blank=True, null=True)
    token = models.CharField(max_length=64, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             blank=True, null=True)
    submissions = models.IntegerField(default=0,
                                      help_text='number of subscriptions')
    successes = models.IntegerField(default=0)
    failures = models.IntegerField(default=0)

    class Meta:
        app_label = 'bitcaster'

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.application = self.event.application
        self.organization = self.application.organization
        super().save(force_insert, force_update, using, update_fields)


class LogEntry(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    application = models.ForeignKey('bitcaster.Application',
                                    related_name='+',
                                    on_delete=models.CASCADE)
    event = models.ForeignKey('bitcaster.Event',
                              related_name='+',
                              on_delete=models.CASCADE)
    subscription = models.ForeignKey('bitcaster.Application',
                                     null=True,
                                     related_name='+',
                                     on_delete=models.SET_NULL)
    channel = models.ForeignKey('bitcaster.Channel',
                                null=True,
                                related_name='+',
                                on_delete=models.SET_NULL)

    class Meta:
        app_label = 'bitcaster'
