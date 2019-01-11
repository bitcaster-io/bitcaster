# -*- coding: utf-8 -*-
import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import Q
from django.template import Template

from bitcaster import logging
from bitcaster.db.fields import DispatcherField, EncryptedJSONField
from bitcaster.exceptions import PluginValidationError
from bitcaster.state import state
from bitcaster.template.secure_context import SecureContext

from .application import Application
from .base import AbstractModel
from .counters import Counter
from .organization import Organization

logger = logging.getLogger(__name__)


class ChannelQuerySet(models.QuerySet):
    def organization_configurable(self, organization):
        return self.filter(organization=organization,
                           application=None,
                           system=False)

    def application_configurable(self, application):
        return self.filter(application=application, system=False)

    def system_configurable(self):
        return self.filter(system=True)

    def selectable(self, application):
        return self.filter(Q(organization=application.organization) |
                           Q(system=True) |
                           Q(application=application))

    def enabled(self, application):
        return self.filter(application=application,
                           )


class Channel(AbstractModel):
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
    handler = DispatcherField()
    # handler = StrategyField(verbose_name='Dispatcher',
    #                         import_error=handler_not_found,
    #                         display_attribute='name',
    #                         registry=dispatcher_registry)
    deprecated = models.BooleanField(default=False)

    objects = ChannelQuerySet().as_manager()

    class Meta:
        app_label = 'bitcaster'
        ordering = ('organization', 'application', 'name')

    def __repr__(self):
        return f'<Channel #{self.id} {self.name}>'

    def __str__(self):
        return self.name

    def validate_subscription(self, subscription):
        try:
            self.handler.validate_subscription(subscription)
        except Exception:
            raise PluginValidationError()

    def validate_message(self, message, **kwargs):
        """

        :param message: Message instance
        :return:
        """
        self.handler.validate_message(message, **kwargs)

    def is_configurable_by(self, user):
        if user.is_superuser:
            return True
        if self.system:
            return user.is_superuser
        if not self.application:
            return

    @property
    def is_configured(self):
        return self.handler.validate_configuration(self.config, False)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if self.system and (self.organization or self.application):
            raise Exception('System channels cannot belong Organization or Application')
        if self.application:
            self.organization = self.application.organization
        self.config = self.handler.get_full_config(self.config)
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
                        'recipient': subscription.subscriber,
                        'today': datetime.datetime.today()})
                    m = body.render(SecureContext(ctx))
                    s = subject.render(SecureContext(ctx))
                    self.handler.emit(subscription, s, m, conn)
                    Counter.objects.increment(subscription)
                    success += 1
                except Exception as e:
                    logger.exception(e)
                    failures += 1
        except ObjectDoesNotExist as e:
            logger.error(e)
            raise ObjectDoesNotExist(f'Unable to find a message for {self}/{event}') from e
        except Exception as e:
            logger.exception(e)
            raise

        return success, failures
