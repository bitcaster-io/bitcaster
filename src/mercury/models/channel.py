# -*- coding: utf-8 -*-
import datetime
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.template import Context, Template

from strategy_field.fields import StrategyField

from mercury import logging
from mercury.dispatchers import dispatcher_registry
from mercury.exceptions import PluginValidationError
from mercury.fields import EncryptedJSONField
from mercury.models import AbstractModel, Application

logger = logging.getLogger(__name__)


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
    enabled = models.BooleanField(default=False)
    description = models.TextField(blank=True, null=True)
    handler = StrategyField(verbose_name='Dispatcher',
                            display_attribute='name',
                            registry=dispatcher_registry)
    deprecated = models.BooleanField(default=False)

    def __repr__(self):
        return "<Channel [{0.pk}] {0.handler}>".format(self, id(self))

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

    def validate_config(self):
        self.handler.config

    # def validate_subscription(self, user):
    #     """
    #         validate user has required
    #     :param user: mercury.models.User
    #     :return:
    #     """
    #     self.handler.validate_subscription(user)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.config = self.handler.get_full_config(self.config)
        super().save(force_insert, force_update, using, update_fields)

    def send(self, subscription, subject, message, *args, **kwargs):
        if not self.enabled:
            logger.error("Channel {0} disabled".format(self))
            return
        logger.debug("Channel [{0.name}] send to {1}".format(self, subscription.subscriber))
        self.handler.validate_subscription(subscription)
        return self.handler.emit(subscription, subject,
                                 message, *args, **kwargs)

    def process_event(self, event, context):
        if not self.enabled:
            logger.error("Channel {0} disabled".format(self))
            return 0, 0
        try:
            message = self.messages.get(event=event)
            body = Template(message.body)
            subject = Template(message.subject)

            logger.debug(f"Processing event {event}")
            conn = self.handler._get_connection()
            success, failures = 0, 0
            for subscription in event.subscriptions.valid(channel=self):
                logger.debug(f"Processing {subscription}")
                try:
                    ctx = dict(context or {})
                    ctx.update({
                        'event': event,
                        'recipient': subscription.subscriber,
                        'today': datetime.datetime.today()})
                    m = body.render(SecureContext(ctx))
                    s = subject.render(SecureContext(ctx))
                    ret = self.handler.emit(subscription, s, m, conn)
                    success += ret
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
            return Wrapper('=====')

        if item in ['key', 'token', 'password']:
            return '******'
        original = getattr(self.__wrapped, item)
        if callable(original):
            return Wrapper(Stop())

        return Wrapper(original)

    def __repr__(self):
        return repr(self.__wrapped)

    def __str__(self):
        return str(self.__wrapped)


class SecureContext(Context):
    def __getitem__(self, key):
        return Wrapper(super().__getitem__(key))
