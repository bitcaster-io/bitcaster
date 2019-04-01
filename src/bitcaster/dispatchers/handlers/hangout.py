# -*- coding: utf-8 -*-
from logging import getLogger

from django.utils.translation import gettext_lazy as _
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
from bitcaster.utils.language import classproperty

logger = getLogger(__name__)


class HangoutMessage(MessageType):
    pass


class HangoutOptions(DispatcherOptions):
    username = serializers.EmailField()
    password = PasswordField()


class HangoutSubscription(SubscriptionOptions):
    recipient = serializers.CharField()


class FireAndForget(EventHandler):
    def __init__(self, local_jid, action, settings):
        self.action = action
        self.client = Client(local_jid, [self], settings)
        self.connected = False

    def run(self):
        self.client.connect()
        self.client.run()

    def disconnect(self):  # pragma: no cover
        self.client.disconnect()
        self.client.run(timeout=2)

    @event_handler(ConnectedEvent)
    def on_connect(self, event):
        self.connected = True

    @event_handler(AuthorizedEvent)
    def handle_authorized(self, event):
        self.action(self.client)
        self.client.disconnect()

    @event_handler(DisconnectedEvent)
    def handle_disconnected(self, event):
        self.connected = False
        return QUIT


@dispatcher_registry.register
class Hangout(CoreDispatcher):
    subscription_class = HangoutSubscription
    options_class = HangoutOptions
    message_class = MessageType
    __help__ = _("""
#### Generate Application password

- Navigate to your [Google Account](https://myaccount.google.com/security).
- Under the Password & sign-in method section, click App passwords.
- If requested login again using your usual password.
- Make sure Other (custom name) is selected in the Select app drop-down menu.
 Type the application name (ie. Bitcaster)
- Click Generate.
""")

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
