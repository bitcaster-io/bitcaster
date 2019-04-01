# -*- coding: utf-8 -*-
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.db.models import F
from strategy_field.utils import fqn

from bitcaster.models.user import User


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
    address = models.CharField(max_length=200, null=True, blank=True)
    subscription = models.ForeignKey('bitcaster.Subscription',
                                     null=True,
                                     related_name='+',
                                     on_delete=models.SET_NULL)
    channel = models.ForeignKey('bitcaster.Channel',
                                null=True,
                                related_name='+',
                                on_delete=models.SET_NULL)
    status = models.BooleanField(help_text='True if successed', default=True)
    info = models.TextField(null=True, blank=True)
    data = JSONField(null=True, blank=True)

    class Meta:
        app_label = 'bitcaster'
