# -*- coding: utf-8 -*-
import hangups
import asyncio
from mercury.dispatchers import serializers
from mercury.dispatchers.base import (Dispatcher, DispatcherOptions,
                                      MessageType, SubscriptionOptions,)
from mercury.dispatchers.registry import dispatcher_registry
from mercury.exceptions import PluginSendError, ValidationError
from mercury.logging import getLogger
from mercury.utils.language import classproperty

logger = getLogger('mercury.plugins.hangout')


class Message(MessageType):
    pass


class Options(DispatcherOptions):
    pass


class RecipientOptions(SubscriptionOptions):
    recipient = serializers.CharField()


@asyncio.coroutine
def send_message(client):
    """Send message using connected hangups.Client instance."""

    # Instantiate a SendChatMessageRequest Protocol Buffer message describing
    # the request.
    request = hangups.hangouts_pb2.SendChatMessageRequest(
        request_header=client.get_request_header(),
        event_request_header=hangups.hangouts_pb2.EventRequestHeader(
            conversation_id=hangups.hangouts_pb2.ConversationId(
                id=CONVERSATION_ID
            ),
            client_generated_id=client.get_client_generated_id(),
        ),
        message_content=hangups.hangouts_pb2.MessageContent(
            segment=[hangups.ChatMessageSegment(MESSAGE).serialize()],
        ),
    )

    try:
        # Make the request to the Hangouts API.
        yield from client.send_chat_message(request)
    finally:
        # Disconnect the hangups Client to make client.connect return.
        yield from client.disconnect()


@dispatcher_registry.register
class Hangout(Dispatcher):
    options_class = Options
    message_class = Message
    subscription_class = RecipientOptions
    __license__ = 'MIT'
    __author__ = 'unknown'

    @classproperty
    def name(cls):
        return 'Hangout'

    def validate_subscription(self, subscription, *args, **kwargs) -> None:
        ser = RecipientOptions(data=subscription.config)
        if not ser.is_valid():
            raise ValidationError(ser.errors)

    def emit(self, subscription, subject, message, *args, **kwargs):
        try:
            recipient = subscription.config['recipient']
            logger.info('Processing {0}'.format(subscription, recipient))

            cookies = hangups.auth.get_auth_stdin(REFRESH_TOKEN_PATH)
            client = hangups.Client(cookies)
            client.on_connect.add_observer(lambda: asyncio.async(send_message(client)))
            loop = asyncio.get_event_loop()
            loop.run_until_complete(client.connect())

        except Exception as e:
            logger.exception(e)
            raise PluginSendError(e)

    def test_connection(self, raise_exception=False):
        raise NotImplementedError
