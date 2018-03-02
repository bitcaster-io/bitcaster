# -*- coding: utf-8 -*-
import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.template import Context, Template
from django.utils.functional import cached_property
from strategy_field.fields import StrategyField

from mercury import logging
from mercury.dispatchers import dispatcher_registry
from mercury.exceptions import HandlerNotFound, PluginValidationError
from mercury.fields import EncryptedJSONField
from mercury.logging import secLog
from mercury.models import AbstractModel, Application
from mercury.models.counters import Counter
from mercury.state import state

logger = logging.getLogger(__name__)


def handler_not_found(fqn, exc):
    try:
        raise HandlerNotFound(fqn) from exc
    except HandlerNotFound as e:
        logger.exception(e)
    return None
    # raise HandlerNotFound(fqn) from exc


class Channel(AbstractModel):
    """ A Channel represent a configured dispatcher.
It can be Global or Application specific.
    """
    name = models.CharField(max_length=255, unique=True)
    application = models.ForeignKey(Application,
                                    null=True,
                                    blank=True,
                                    on_delete=models.CASCADE,
                                    related_name='owned_channels')
    config = EncryptedJSONField(null=True, blank=True)
    # configured = models.BooleanField(default=False)
    enabled = models.BooleanField(default=False)
    description = models.TextField(blank=True, null=True)
    handler = StrategyField(verbose_name='Dispatcher',
                            import_error=handler_not_found,
                            display_attribute='name',
                            registry=dispatcher_registry)
    deprecated = models.BooleanField(default=False)

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

    # def validate_config(self):
    #     self.handler.config

    # def validate_subscription(self, user):
    #     """
    #         validate user has required
    #     :param user: mercury.models.User
    #     :return:
    #     """
    #     self.handler.validate_subscription(user)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.config = self.handler.get_full_config(self.config)
        # self.configured = self.handler.validate_config(self.config)
        super().save(force_insert, force_update, using, update_fields)

    # def send(self, subscription, subject, message, *args, **kwargs):
    #     if not self.enabled:
    #         logger.error("Channel {0} disabled".format(self))
    #         return
    #     logger.debug("Channel [{0.name}] send to {1}".format(self, subscription.subscriber))
    #     self.handler.validate_subscription(subscription)
    #     return self.handler.emit(subscription, subject,
    #                              message, *args, **kwargs)

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


class Stop:
    def __repr__(self):
        return ""

    def __str__(self):
        return ""


class Wrapper:
    def __init__(self, wrapped):
        self.__wrapped = wrapped

    def _path(self):
        pass

    def __getattr__(self, item):
        if isinstance(self.__wrapped, Stop):
            return Wrapper('*******')

        if item in ['key', 'token', 'password', 'handler', 'owner']:
            secLog.error(f'Access forbidden attribute `{item}`',
                         extra={'attribute': item,
                                'object': self.__wrapped})
            return '******'
        original = getattr(self.__wrapped, item)
        if callable(original):
            secLog.error(f'Access forbidden attribute `{item}`',
                         extra={'attribute': item,
                                'object': self.__wrapped})
            return Wrapper(Stop())

        return Wrapper(original)

    def __repr__(self):
        return repr(self.__wrapped)

    def __str__(self):
        return str(self.__wrapped)


class SecureContext(Context):
    def __getitem__(self, key):
        return Wrapper(super().__getitem__(key))
