import logging
import poplib
import re

from crashlog.middleware import process_exception
from django.utils.functional import cached_property
from django.utils.translation import gettext as _

from bitcaster.agents import serializers
from bitcaster.agents.handlers.mail import ImapMessage, Pop3Message
from bitcaster.api.fields import PasswordField, RegexField

from ..base import Agent, AgentOptions
from ..registry import agent_registry

logger = logging.getLogger(__name__)


class Pop3Options(AgentOptions):
    server = serializers.CharField()
    port = serializers.IntegerField()
    ssl = serializers.BooleanField(default=False)
    timeout = serializers.IntegerField(default=10)
    authentication = serializers.ChoiceField(choices=((1, 'Standard'),
                                                      (2, 'APOP'),
                                                      (3, 'RPOP')),
                                             default=1, label='Use APOP authentication')
    username = serializers.CharField(allow_blank=True,
                                     required=False)
    password = PasswordField(allow_blank=True, required=False)

    body_regex = RegexField(allow_blank=True, required=False,
                            help_text='message body regular expression')
    subject_regex = RegexField(allow_blank=True, required=False)
    sender_regex = RegexField(allow_blank=True, required=False)
    to_regex = RegexField(allow_blank=True, required=False)

    fieldset_defs = (
        ('event', ['event', ]),
        ('server', ['server', 'port', 'ssl', 'timeout']),
        ('authentication', ['authentication', 'username', 'password']),
        ('filters', ['body_regex', 'subject_regex', 'sender_regex', 'to_regex']),)

    def get_agent(self):
        return Pop3Agent


@agent_registry.register
class Pop3Agent(Agent):  # pragma: no cover
    options_class = Pop3Options
    icon = 'mail-pop3.png'

    def _get_connection(self, config=None) -> poplib.POP3:  # pragma: no cover
        config = config or self.config
        if config['ssl']:
            pop3 = poplib.POP3_SSL(config['server'], config['port'], timeout=config['timeout'])
        else:
            pop3 = poplib.POP3(config['server'], config['port'], config['timeout'])
        if config['authentication'] == 1:
            pop3.user(config['username'])
            pop3.pass_(config['password'])
        elif config['authentication'] == 2:
            pop3.apop(config['username'], config['password'])
        elif config['authentication'] == 3:
            pop3.rpop(config['username'])

        return pop3

    def get_usage(self):
        return 'Simply set credentials and folder to check'

    @cached_property
    def event(self):
        from bitcaster.models import Event
        return Event.objects.get(pk=self.config['event'])

    @cached_property
    def subject_regex(self):
        return re.compile(self.config['subject_regex'])

    @cached_property
    def sender_regex(self):
        return re.compile(self.config['sender_regex'])

    @cached_property
    def body_regex(self):
        return re.compile(self.config['body_regex'])

    @cached_property
    def recipient_regex(self):
        return re.compile(self.config['to_regex'])

    def filter(self, message: ImapMessage):
        if self.subject_regex and not self.subject_regex.match(message.subject):
            return False
        if self.sender_regex and not self.sender_regex.match(message.sender):
            return False
        if self.recipient_regex and not self.recipient_regex.match(message.recipient):
            return False
        if self.body_regex and not self.body_regex.match(message.text):
            return False

        return True

    def trigger(self, payload=None):
        from bitcaster.models.occurence import Occurence
        from bitcaster.tsdb.api import log_new_occurence, log_monitor_trigger, log_monitor_error
        from bitcaster.tasks.event import trigger_event

        if not self.event.enabled:
            msg = _("Monitor %(monitor)s cannot trigger disabled event '%(event)s'" % dict(monitor=self,
                                                                                           event=self.event))
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
                                 })
            return True
        except Exception as e:
            logger.error(e)
            process_exception(e)

    def _check_result(self, result):
        if result[0] != 'OK':
            raise Exception(''.join(result[1]))

    def apply_policy(self, conn, num):
        pass

    def get_matched_elements(self, connection=None):
        conn = connection or self._get_connection()
        resp, mails, octets = conn.list()
        numMessages = len(mails)

        ret = []
        for i in range(numMessages):
            mail = conn.retr(i + 1)
            message = Pop3Message(mail)
            if self.filter(message):
                ret.append(message)
        return ret

    def poll(self, trigger=True):  # pragma: no cover
        from bitcaster.tsdb.api import log_monitor_poll
        conn = self._get_connection()
        resp, mails, octets = conn.list()
        numMessages = len(mails)

        ret = []
        for num in range(numMessages):
            mail = conn.retr(num + 1)
            message = Pop3Message(mail)
            if self.filter(message):
                if trigger and self.trigger(message):
                    ret += 1
                    self.apply_policy(conn, num)

        log_monitor_poll(self.owner)
        return ret

    def test_connection(self, raise_exception=False):  # pragma: no cover
        try:
            pop3 = self._get_connection()
            pop3.getwelcome()
            return True
        except (Exception, poplib.error_proto):
            if raise_exception:
                raise
            return False
