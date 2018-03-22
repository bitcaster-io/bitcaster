# -*- coding: utf-8 -*-
from django.db import models

from bitcaster import logging

from .application import Application
from .base import AbstractModel
from .channel import Channel
from .event import Event

logger = logging.getLogger(__name__)

LANGUAGES = (('all', 'All'),
             ('it', 'Italian'),
             ('fr', 'French'),
             ('es', 'Spanish'),
             ('en', 'English'))


class Message(AbstractModel):
    name = models.CharField(max_length=100)
    application = models.ForeignKey(Application, editable=False,
                                    on_delete=models.CASCADE,
                                    related_name='messages')
    event = models.ForeignKey(Event,
                              on_delete=models.CASCADE,
                              related_name='messages')
    channel = models.ForeignKey(Channel,
                                on_delete=models.CASCADE,
                                related_name='messages')
    language = models.CharField(choices=LANGUAGES,
                                default='all',
                                max_length=3)

    subject = models.CharField(max_length=100,
                               default='',
                               blank=True, null=False)
    body = models.TextField()
    html = models.TextField()

    class Meta:
        unique_together = ('event', 'channel', 'language')

    def __str__(self):
        return self.name

    def parse_body(self, ctx):
        return self.body.format(**ctx)

        # if self.pk and self.channels.exclude(application=self.event.application).exists():
        # if self.pk and Message.objects.filter(event=self.event,
        #                                       channels__in=self.channels.all()).exclude(pk=self.pk).exists():
        #     raise ValidationError('A Message for this channel already exists')

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.application = self.event.application
        super().save(force_insert, force_update, using, update_fields)

    def clean(self):

        self.channel.validate_message(self)
