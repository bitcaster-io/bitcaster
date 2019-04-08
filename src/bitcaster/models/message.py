# -*- coding: utf-8 -*-
import logging

from django.db import models
from django.utils.translation import gettext_lazy as _

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

    enabled = models.BooleanField(default=False)

    subject = models.CharField(max_length=100,
                               default='',
                               blank=True, null=False)
    body = models.TextField()
    html = models.TextField(blank=True, null=True)

    class Meta:
        app_label = 'bitcaster'
        unique_together = ('event', 'channel', 'language')
        verbose_name = _('Message')
        verbose_name_plural = _('Messages')

    class Reverse:
        pattern = 'app-key-{op}'
        args = ['application.organization.slug', 'application.slug', 'id']
        verbose_name = _('Message')
        verbose_name_plural = _('Messages')

    def __str__(self):
        return '%s %s' % (self.channel, self.event)

    def parse_body(self, ctx):
        return self.body.format(**ctx)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.application = self.event.application
        assert self.channel.organization == self.application.organization
        super().save(force_insert, force_update, using, update_fields)
        # if not self.enabled:
        #     self.event.check_enabled()

    def clean(self):
        if self.enabled:
            self.channel.validate_message(self)
