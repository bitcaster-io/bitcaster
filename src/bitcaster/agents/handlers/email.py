import imaplib
import logging
import re
from email import message_from_string

from django.utils.functional import cached_property

from bitcaster.agents import serializers
from bitcaster.api.fields import PasswordField, RegexField

from ..base import Agent, AgentOptions
from ..registry import agent_registry

logger = logging.getLogger(__name__)


class EmailMessage:
    def __init__(self, email):
        self.raw_email = email
        raw_email_string = email.decode('utf-8')
        self.email_message = message_from_string(raw_email_string)

    @property
    def subject(self):
        return self.email_message.get('subject')

    @property
    def sender(self):
        return self.email_message.get('sender')

    @property
    def recipient(self):
        return self.email_message.get('to')

    @property
    def text(self):
        body = ''
        for part in self.email_message.walk():
            if part.get_content_type() == 'text/plain':
                body = part.get_payload(decode=True)
            else:
                continue
        return body


class EmailAbstractOptions(AgentOptions):
    username = serializers.CharField(allow_blank=True, required=False)
    password = PasswordField(allow_blank=True, required=False)
    folder = serializers.CharField(initial='inbox')
    body_regex = RegexField(allow_blank=True, required=False,
                            help_text='-----')
    subject_regex = RegexField(allow_blank=True, required=False)
    sender_regex = RegexField(allow_blank=True, required=False)
    to_regex = RegexField(allow_blank=True, required=False)


class EmailOptions(EmailAbstractOptions):
    server = serializers.CharField()
    port = serializers.IntegerField()
    tls = serializers.BooleanField(default=False)


@agent_registry.register
class EmailAgent(Agent):
    options_class = EmailOptions

    def _get_connection(self) -> object:
        config = self.config
        if config['tls']:
            imap = imaplib.IMAP4_SSL(host=config['server'],
                                     port=config['port'])
        else:
            imap = imaplib.IMAP4(host=config['server'],
                                 port=config['port'])
        imap.login(config['username'], config['password'])
        return imap

    def get_usage(self, config):
        return ''

    @cached_property
    def event(self):
        return self.config['event']

    def filter(self, message: EmailMessage):
        if self.subject_regex.match(message.subject):
            return True
        return False

    def trigger(self, payload=None):
        logger.info(payload.subject)
        logger.info(f'Monitor {self.name} trigger event {self.event}')
        pass

    def poll(self):
        self.subject_regex = re.compile(self.config['subject_regex'])
        self.sender_regex = re.compile(self.config['sender_regex'])
        self.body_regex = re.compile(self.config['body_regex'])

        conn = self._get_connection()
        conn.select(self.config['folder'])
        type, data = conn.search(None, 'ALL')

        for num in reversed(data[0].split()):
            typ, data = conn.fetch(num, '(BODY.PEEK[])')
            message = EmailMessage(data[0][1])
            if self.filter(message):
                self.trigger(message)

    def test_connection(self, raise_exception=False):
        try:
            self._get_connection()
            return True
        except Exception:
            if raise_exception:
                raise
            return False
