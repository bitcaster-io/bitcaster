import imaplib
import logging
import re
from email import message_from_string

from crashlog.middleware import process_exception
from django.utils.functional import cached_property
from django.utils.translation import gettext as _

from bitcaster.agents import serializers
from bitcaster.api.fields import PasswordField, RegexField

from ..base import Agent, AgentOptions
from ..registry import agent_registry

logger = logging.getLogger(__name__)

pattern_uid = re.compile(r'\d+ \(UID (?P<uid>\d+)\)')


def parse_uid(data):
    match = pattern_uid.match(data)
    return match.group('uid')


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
    def text(self):  # pragma: no cover
        body = ''
        for part in self.email_message.walk():
            if part.get_content_type() == 'text/plain':
                body = part.get_payload(decode=True)
            else:
                continue
        return body


class EmailAbstractOptions(AgentOptions):
    MOVE = 1
    DELETE = 2
    READ = 3

    username = serializers.CharField(allow_blank=True,

                                     required=False)
    password = PasswordField(allow_blank=True, required=False)
    folder = serializers.CharField(initial='inbox')
    unseen = serializers.BooleanField(required=False,
                                      default=False,
                                      help_text='Only check unread email')
    policy = serializers.ChoiceField(((MOVE, _('Move processed')),
                                      (DELETE, _('Delete processed')),
                                      (READ, _('Mark as read')),
                                      ), )

    processed_folder = serializers.CharField(default='processed')

    body_regex = RegexField(allow_blank=True, required=False,
                            help_text='message body regular expression')
    subject_regex = RegexField(allow_blank=True, required=False)
    sender_regex = RegexField(allow_blank=True, required=False)
    to_regex = RegexField(allow_blank=True, required=False)


class EmailOptions(EmailAbstractOptions):
    server = serializers.CharField()
    port = serializers.IntegerField()
    tls = serializers.BooleanField(default=False)


@agent_registry.register
class EmailAgent(Agent):  # pragma: no cover
    options_class = EmailOptions

    def _get_connection(self) -> imaplib.IMAP4:  # pragma: no cover
        config = self.config
        if config['tls']:
            imap = imaplib.IMAP4_SSL(host=config['server'],
                                     port=config['port'])
        else:
            imap = imaplib.IMAP4(host=config['server'],
                                 port=config['port'])
        imap.login(config['username'], config['password'])
        return imap

    def get_usage(self):
        return 'Simply set credentials and folder to check'

    @cached_property
    def event(self):
        from bitcaster.models import Event
        return Event.objects.get(pk=self.config['event'])

    def filter(self, message: EmailMessage):
        if self.subject_regex.match(message.subject):
            return True
        return False

    def trigger(self, payload=None):
        from bitcaster.models.occurence import Occurence
        from bitcaster.tsdb.api import log_new_occurence, log_monitor_trigger, log_monitor_error
        from bitcaster.tasks.event import trigger_event

        if not self.event.enabled:
            msg = f"Monitor {self.name} cannot trigger disabled event '{self.event}'"
            logger.error(msg)
            log_monitor_error(self.owner, msg)
            return

        logger.info(f"Monitor {self.name} trigger event '{self.event}'")
        occurence = Occurence.log(event=self.event)
        log_monitor_trigger(self.owner)
        log_new_occurence(occurence)
        try:
            trigger_event.delay(occurence.pk,
                                {'message': payload.text.decode(),
                                 'subject': payload.subject,
                                 'sender': payload.sender,
                                 'recipient': payload.recipient,
                                 },
                                )
            return True
        except Exception as e:
            logger.error(e)
            process_exception(e)

    def _check_result(self, result):
        if result[0] != 'OK':
            raise Exception(''.join(result[1]))

    def apply_policy(self, conn, num):
        resp, data = conn.fetch(num, '(UID)')
        msg_uid = parse_uid(data[0].decode())
        try:
            if self.config['policy'] == EmailOptions.READ:
                result = conn.uid('STORE', msg_uid, '+FLAGS', r'(\Seen)')
                self._check_result(result)
            elif self.config['policy'] == EmailOptions.MOVE:
                result = conn.uid('COPY', msg_uid, self.config['processed_folder'])
                self._check_result(result)

                result = conn.uid('STORE', msg_uid, '+FLAGS', r'(\Deleted)')
                self._check_result(result)
                conn.expunge()
            elif self.config['policy'] == EmailOptions.DELETE:
                result = conn.uid('STORE', msg_uid, '+FLAGS', r'(\Deleted)')
                self._check_result(result)
                conn.expunge()
        except Exception as e:
            from bitcaster.tsdb.api import log_monitor_error
            log_monitor_error(self.owner, str(e))

    def poll(self, trigger=True):  # pragma: no cover
        from bitcaster.tsdb.api import log_monitor_poll
        self.subject_regex = re.compile(self.config['subject_regex'])
        self.sender_regex = re.compile(self.config['sender_regex'])
        self.body_regex = re.compile(self.config['body_regex'])
        ret = 0
        conn = self._get_connection()
        conn.select(self.config['folder'])
        if self.config['unseen']:
            filter = 'UnSeen'
        else:
            filter = 'ALL'
        type, data = conn.search(None, filter)

        for num in reversed(data[0].split()):
            typ, data = conn.fetch(num, '(BODY.PEEK[])')
            message = EmailMessage(data[0][1])
            if self.filter(message):
                if trigger and self.trigger(message):
                    ret += 1
                    self.apply_policy(conn, num)

        log_monitor_poll(self.owner)
        return ret

    def test_connection(self, raise_exception=False):  # pragma: no cover
        try:
            self._get_connection()
            return True
        except Exception:
            if raise_exception:
                raise
            return False
