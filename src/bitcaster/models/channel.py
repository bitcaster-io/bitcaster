# -*- coding: utf-8 -*-
import datetime

from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import models
from django.db.models import Q
from django.template import Template
from django.utils.translation import gettext_lazy as _

from bitcaster import logging
from bitcaster.db.fields import DispatcherField, EncryptedJSONField
from bitcaster.exceptions import MaxChannelError, PluginValidationError
from bitcaster.models.mixins import ReverseWrapperMixin
from bitcaster.state import state
from bitcaster.template.secure_context import SecureContext

from .application import Application
from .base import AbstractModel
from .counters import Counter, LogEntry
from .organization import Organization

logger = logging.getLogger(__name__)


class ChannelQuerySet(models.QuerySet):
    def valid(self):
        # for c in self.all():
        #     try:
        #         assert c.handler
        #     except Exception:
        #         c.handler = None
        #         c.enabled = False
        #         c.save()
        return self.all()

    # def organization_configurable(self, organization):
    #     return self.filter(organization=organization,
    #                        application=None,
    #                        system=False)
    #
    # def application_configurable(self, application):
    #     return self.filter(application=application, system=False)
    #
    # def system_configurable(self):
    #     return self.filter(system=True)
    #
    def selectable(self, application):
        return self.filter(Q(organization=application.organization) |
                           Q(system=True) |
                           Q(application=application))

    # def enabled(self, application):
    #     return self.filter(application=application,
    #                        )


class Channel(ReverseWrapperMixin, AbstractModel):
    """ A Channel represent a configured dispatcher.
It can be Global or Application specific.
    """
    name = models.CharField(max_length=255)
    organization = models.ForeignKey(Organization,
                                     null=True,
                                     blank=True,
                                     on_delete=models.CASCADE)
    application = models.ForeignKey(Application,
                                    null=True,
                                    blank=True,
                                    on_delete=models.CASCADE)
    system = models.BooleanField(default=False)
    config = EncryptedJSONField(null=True, blank=True)
    enabled = models.BooleanField(default=False)
    description = models.TextField(blank=True, null=True)
    handler = DispatcherField(null=True)
    deprecated = models.BooleanField(default=False)
    errors_threshold = models.IntegerField(default=100,
                                           help_text='Number or errors before channel will be automatically disabled')
    objects = ChannelQuerySet().as_manager()

    class Meta:
        app_label = 'bitcaster'
        ordering = ('organization', 'application', 'name')
        verbose_name = _('Channel')
        verbose_name_plural = _('Channels')

    class Reverse:
        pattern = 'org-channel-{op}'
        args = ['organization.slug', 'id']

    def __repr__(self):
        return f'<Channel #{self.id} {self.name}>'

    def __str__(self):
        return self.name

    def validate_address(self, address):
        try:
            return self.handler.validate_address(address)
        except Exception:
            raise PluginValidationError()

    def validate_subscription(self, subscription):
        try:
            return self.handler.validate_subscription(subscription)
        except Exception:
            raise PluginValidationError()

    def validate_message(self, message, **kwargs):
        self.handler.validate_message(message, **kwargs)

    def get_usage_message(self):
        return self.handler.get_usage_message(self.config)

    def get_usage(self):
        return self.handler.get_usage(self.config)

    # def is_configurable_by(self, user):
    #     if user.is_superuser:
    #         return True
    #     if self.system:
    #         return user.is_superuser
    #     if not self.application:
    #         return
    #
    @property
    def is_configured(self):
        if self.handler:
            return self.handler.validate_configuration(self.config, False)
        return False

    def clean(self):
        if not self.handler and self.enabled:
            raise ValidationError('Cannot enable Channel without handler')
        if self.enabled:
            if not self.config:
                raise ValidationError('Channel must be configured')
            elif not self.is_configured:
                raise ValidationError('Configure channel before enable it')

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        # if self.application:
        #     self.organization = self.application.organization
        # if self.handler:
        #     self.config = self.handler.get_full_config(self.config)
        super().save(force_insert, force_update, using, update_fields)

    def process_event(self, event, context):
        if not self.enabled:
            logger.error('Channel {0} disabled'.format(self))
            return 0, 0
        try:
            message = self.messages.get(event=event)
            body = Template(message.body)
            subject = Template(message.subject)
            state.data['event'] = event
            # logger.debug(f"Processing event {event}")
            conn = self.handler._get_connection()
            success, failures = 0, 0
            for subscription in event.subscriptions.valid(channel=self):
                state.data['subscription'] = subscription
                logger.debug(f'Processing {subscription}')
                try:
                    ctx = dict(context or {})
                    ctx.update({
                        'event': event,
                        'channel': self,
                        'application': self.application,
                        'organization': self.organization,
                        'subscription': subscription,
                        'recipient': subscription.subscriber,
                        'today': datetime.datetime.today()})
                    m = body.render(SecureContext(ctx))
                    s = subject.render(SecureContext(ctx))
                    self.handler.emit(subscription, s, m, conn)
                    Counter.objects.increment(subscription)
                    success += 1
                    LogEntry.objects.create(event=event,
                                            channel=self,
                                            subscription=subscription,
                                            application=event.application)
                except Exception as e:
                    logger.exception(e)
                    LogEntry.objects.create(event=event,
                                            subscription=subscription,
                                            application=event.application,
                                            channel=self,
                                            status=False,
                                            info=str(e))
                    failures += 1
                if failures > self.errors_threshold:
                    raise MaxChannelError(self)
        except MaxChannelError as e:
            logger.error(e)
            self.enabled = False
            self.save()
            raise
        except ObjectDoesNotExist as e:
            logger.error(e)
            raise ObjectDoesNotExist(f'Unable to find a message for {self}/{event}') from e
        except Exception as e:
            logger.exception(e)
            raise

        return success, failures
