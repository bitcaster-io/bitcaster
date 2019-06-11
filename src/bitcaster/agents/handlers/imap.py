import datetime
import imaplib
import logging
import re

from crashlog.middleware import process_exception
from django.utils.functional import cached_property
from django.utils.translation import gettext as _
from rest_framework.exceptions import ValidationError

from bitcaster.agents import serializers
from bitcaster.agents.handlers.mail import (ImapMessage,
                                            parse_list_response, parse_uid,)
from bitcaster.api.fields import PasswordField, RegexField

from ..base import Agent, AgentOptions
from ..registry import agent_registry

logger = logging.getLogger(__name__)


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
                                      ),
                                     default=READ)

    processed_folder = serializers.CharField(default='processed')

    body_regex = RegexField(allow_blank=True, required=False,
                            help_text='message body regular expression')
    subject_regex = RegexField(allow_blank=True, required=False)
    sender_regex = RegexField(allow_blank=True, required=False)
    to_regex = RegexField(allow_blank=True, required=False)

    def get_agent(self):
        raise NotImplementedError

    def validate(self, attrs):
        errs = {}
        try:
            agent = self.get_agent()()
            config = agent.get_full_config(attrs)
            conn = agent._get_connection(config)
            typ, data = conn.list()
            folders = [parse_list_response(e)[2] for e in data]
            if config['folder'] not in folders:
                errs['folder'] = 'Invalid folder. Valid choices are: %s' % ', '.join(folders)
            if config['policy'] == self.MOVE:
                if config['folder'] in folders:
                    folders.remove(config['folder'])
                if config['processed_folder'] not in folders:
                    errs['processed_folder'] = 'Invalid folder. Valid choices are: %s' % ', '.join(folders)
        except imaplib.IMAP4.error as e:
            raise ValidationError({'username': str(e)})
        except Exception as e:
            logger.exception(e)
            process_exception(e)
            raise ValidationError(str(e))

        if errs:
            raise ValidationError(errs)
        return attrs


class EmailOptions(EmailAbstractOptions):
    server = serializers.CharField()
    port = serializers.IntegerField()
    tls = serializers.BooleanField(default=False)

    def get_agent(self):
        return ImapAgent


@agent_registry.register
class ImapAgent(Agent):  # pragma: no cover
    options_class = EmailOptions
    icon = 'mail-imap.png'

    def _get_connection(self, config=None) -> imaplib.IMAP4:  # pragma: no cover
        config = config or self.config
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

    def get_matched_elements(self, connection=None):
        conn = connection or self._get_connection()
        conn.select(self.config['folder'])
        date = (datetime.date.today() - datetime.timedelta(hours=1)).strftime('%d-%b-%Y')

        if self.config['unseen']:
            seen = ' (UnSeen)'
        else:
            seen = ''

        filter = f'(SENTSINCE {date}){seen}'

        type, data = conn.search(None, filter)
        ret = []
        for num in reversed(data[0].split()):
            # typ, data = conn.fetch(num, '(BODY.PEEK[])')
            typ, data = conn.fetch(num, '(BODY.PEEK[] UID)')
            message = ImapMessage(data[0][1])
            if self.filter(message):
                ret.append(message)
        return ret

    def poll(self, trigger=True):  # pragma: no cover
        from bitcaster.tsdb.api import log_monitor_poll
        ret = 0
        conn = self._get_connection()
        conn.select(self.config['folder'])
        date = (datetime.date.today() - datetime.timedelta(hours=10)).strftime('%d-%b-%Y')

        if self.config['unseen']:
            seen = ' (UnSeen)'
        else:
            seen = ''

        filter = f'(SENTSINCE {date}){seen}'
        type, data = conn.search(None, filter)

        for num in reversed(data[0].split()):
            typ, data = conn.fetch(num, '(BODY.PEEK[] UID)')
            message = ImapMessage(data[0][1])
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
