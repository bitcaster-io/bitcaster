from logging import getLogger

from django.utils.translation import gettext_lazy as _
from pyxmpp2.client import Client
from pyxmpp2.clientstream import ClientStream
from pyxmpp2.jid import JID
from pyxmpp2.mainloop.interfaces import QUIT, EventHandler, event_handler
from pyxmpp2.message import Message
from pyxmpp2.settings import XMPPSettings
from pyxmpp2.streamevents import (AuthorizedEvent, ConnectedEvent,
                                  DisconnectedEvent,)
from pyxmpp2.transport import TCPTransport

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


class BitcasterClient(Client):
    def connect(self):
        """Schedule a new XMPP c2s connection.
        """
        with self.lock:
            if self.stream:
                logger.debug('Closing the previously used stream.')
                self._close_stream()

            transport = TCPTransport(self.settings)

            addr = self.settings['server']
            service = self.settings['c2s_service']

            transport.connect(addr, self.settings['c2s_port'], service)
            handlers = self._base_handlers[:]
            handlers += self.handlers + [self]
            self.clear_response_handlers()
            self.setup_stanza_handlers(handlers, 'pre-auth')
            stream = ClientStream(self.jid, self, handlers, self.settings)
            stream.initiate(transport)
            self.main_loop.add_handler(transport)
            self.main_loop.add_handler(stream)
            self._ml_handlers += [transport, stream]
            self.stream = stream
            self.uplink = stream


class FireAndForget(EventHandler):
    def __init__(self, local_jid, action, settings):
        self.action = action
        self.client = BitcasterClient(local_jid, [self], settings)
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
    message_class = HangoutMessage
    __help__ = _("""
#### Generate Application password

- Navigate to your [Google Account](https://myaccount.google.com/security).
- Under the Password & sign-in method section, click App passwords.
- If requested login again using your usual password.
- Make sure Other (custom name) is selected in the Select app drop-down menu.
 Type the application name (ie. Bitcaster)
- Click Generate.
- Do not forget to check `Access for less secure app`
""")

    @classproperty
    def name(cls):
        return 'Hangout'

    def _get_connection(self) -> FireAndForget:
        settings = XMPPSettings({'starttls': True,
                                 'password': self.config['password'],
                                 'server': 'gmail.com',
                                 'c2s_service': 'xmpp-client',
                                 'c2s_port': 5222,
                                 # 'default_stanza_timeout': 30,
                                 'tls_verify_peer': False})
        source_jid = JID(self.config['username'])

        return FireAndForget(source_jid, None, settings)

    def emit(self, address: str, subject: str, message: str,
             connection=None, *args, **kwargs) -> str:
        try:
            logger.debug(f"Processing '{address}'")
            conn = connection or self._get_connection()

            target_jid = JID(address)

            msg = Message(to_jid=target_jid, body=message, subject=subject, stanza_type='chat')

            conn.action = lambda c: c.stream.send(msg)
            conn.run()
            return address
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
