# -*- coding: utf-8 -*-
from pyxmpp2.client import Client
from pyxmpp2.jid import JID
from pyxmpp2.mainloop.interfaces import QUIT, EventHandler, event_handler
from pyxmpp2.message import Message
from pyxmpp2.settings import XMPPSettings
from pyxmpp2.streamevents import (AuthorizedEvent, ConnectedEvent,
                                  DisconnectedEvent,)

from bitcaster.api.fields import PasswordField
from bitcaster.dispatchers import serializers
from bitcaster.dispatchers.base import (CoreDispatcher, DispatcherOptions,
                                        MessageType, SubscriptionOptions,)
from bitcaster.dispatchers.registry import dispatcher_registry
from bitcaster.exceptions import PluginSendError
from bitcaster.logging import getLogger
from bitcaster.utils.language import classproperty

logger = getLogger(__name__)


class HangoutMessage(MessageType):
    pass


class HangoutOptions(DispatcherOptions):
    username = serializers.CharField()
    password = PasswordField()


class HangoutSubscription(SubscriptionOptions):
    recipient = serializers.CharField()


class FireAndForget(EventHandler):
    """A minimal XMPP client that just connects to a server
    and runs single function.

    :Ivariables:
        - `action`: the function to run after the stream is authorized
        - `client`: a `Client` instance to do the rest of the job
    :Types:
        - `action`: a callable accepting a single 'client' argument
        - `client`: `pyxmpp2.client.Client`
    """

    def __init__(self, local_jid, action, settings):
        self.action = action
        self.client = Client(local_jid, [self], settings)
        self.connected = False

    def run(self):
        """Request client connection and start the main loop."""
        self.client.connect()
        self.client.run()

    def disconnect(self):
        """Request disconnection and let the main loop run for a 2 more
        seconds for graceful disconnection."""
        self.client.disconnect()
        self.client.run(timeout=2)

    @event_handler(ConnectedEvent)
    def on_connect(self, event):
        self.connected = True

    @event_handler(AuthorizedEvent)
    def handle_authorized(self, event):
        """Send the initial presence after log-in."""
        # pylint: disable=W0613
        if self.action:
            self.action(self.client)
            self.client.disconnect()

    @event_handler(DisconnectedEvent)
    def handle_disconnected(self, event):
        """Quit the main loop upon disconnection."""
        # pylint: disable=W0613,R0201
        self.connected = False
        return QUIT


@dispatcher_registry.register
class Hangout(CoreDispatcher):
    subscription_class = HangoutSubscription
    options_class = HangoutOptions
    message_class = MessageType

    @classproperty
    def name(cls):
        return 'Hangout'

    # def validate_subscription(self, subscription, *args, **kwargs) -> None:
    #     ser = HangoutSubscription(data=subscription.config)
    #     if not ser.is_valid():
    #         raise PluginValidationError(ser.errors)

    def _get_connection(self) -> FireAndForget:
        settings = XMPPSettings({'starttls': True,
                                 'password': self.config['password'],
                                 'tls_verify_peer': False})
        source_jid = JID(self.config['username'])

        return FireAndForget(source_jid, None, settings)

    def emit(self, subscription: object, subject: str, message: str,
             connection=None, *args, **kwargs) -> int:
        try:
            recipient = self.get_recipient_address(subscription)
            logger.debug(f"Processing {subscription} '{recipient}'")
            conn = connection or self._get_connection()

            target_jid = JID(recipient)

            msg = Message(to_jid=target_jid, body=message, subject=subject, stanza_type='chat')

            conn.action = lambda c: c.stream.send(msg)
            conn.run()
            return 1
        except Exception as e:
            logger.exception(e)
            raise PluginSendError(e)

    def test_connection(self, raise_exception=False):
        conn = self._get_connection()
        success = False

        def check(client):
            nonlocal success
            success = True

        conn.action = check
        try:
            conn.run()
            return success
        except Exception as e:
            logger.exception(e)
            return False
