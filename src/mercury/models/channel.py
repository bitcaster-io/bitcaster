# -*- coding: utf-8 -*-
import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.template import Template
from django.utils.functional import cached_property
from strategy_field.fields import StrategyField

from mercury import logging
from mercury.db.fields import EncryptedJSONField
from mercury.dispatchers import dispatcher_registry
from mercury.exceptions import HandlerNotFound, PluginValidationError
from mercury.state import state
from mercury.template.secure_context import SecureContext

from .application import Application
from .base import AbstractModel
from .counters import Counter
from .organization import Organization

logger = logging.getLogger(__name__)


def handler_not_found(fqn, exc):
    try:
        raise HandlerNotFound(fqn) from exc
    except HandlerNotFound as e:
        logger.exception(e)
    return None


class Channel(AbstractModel):
    """ A Channel represent a configured dispatcher.
It can be Global or Application specific.
    """
    name = models.CharField(max_length=255)
    organization = models.ForeignKey(Organization,
                                     null=True,
                                     blank=True,
                                     on_delete=models.CASCADE,
                                     related_name='channels')
    application = models.ForeignKey(Application,
                                    null=True,
                                    blank=True,
                                    on_delete=models.CASCADE,
                                    related_name='channels')
    system = models.BooleanField(default=False)
    config = EncryptedJSONField(null=True, blank=True)
    enabled = models.BooleanField(default=False)
    description = models.TextField(blank=True, null=True)
    handler = StrategyField(verbose_name='Dispatcher',
                            import_error=handler_not_found,
                            display_attribute='name',
                            registry=dispatcher_registry)
    deprecated = models.BooleanField(default=False)

    class Meta:
        ordering = ('organization', 'application', 'name')

    def __repr__(self):
        return f"<Channel #{self.id} {self.name}>"

    def __str__(self):
        return self.name

    def validate_subscription(self, subscription):
        try:
            self.handler.validate_subscription(subscription)
        except Exception:
            raise PluginValidationError()

    def validate_message(self, message):
        """

        :param message: Message instance
        :return:
        """

    @cached_property
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
            logger.error("Channel {0} disabled".format(self))
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
                logger.debug(f"Processing {subscription}")
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
            raise ObjectDoesNotExist(f"Unable to find a message for {self}/{event}") from e
        except Exception as e:
            logger.exception(e)
            raise

        return success, failures
