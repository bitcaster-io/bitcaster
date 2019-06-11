import re
from email import message_from_bytes

from django.utils.functional import cached_property

pattern_uid = re.compile(r'\d+ \(UID (?P<uid>\d+)\)')


def parse_uid(data):
    match = pattern_uid.match(data)
    return match.group('uid')


class ImapMessage:
    def __init__(self, email):
        self.raw_email = email

    @cached_property
    def email_message(self):
        return message_from_bytes(self.raw_email)

    @property
    def id(self):
        return hash(self.email_message['Message-ID'])

    @property
    def subject(self):
        return self.email_message.get('subject')

    @property
    def sender(self):
        return self.email_message.get('from')

    @property
    def recipient(self):
        return self.email_message.get('to')

    @property
    def date(self):
        return self.email_message.get('Date')

    @property
    def text(self):  # pragma: no cover
        body = ''
        for part in self.email_message.walk():
            if part.get_content_type() == 'text/plain':
                body = part.get_payload(decode=False)
            else:
                continue
        return body


class Pop3Message(ImapMessage):
    def __init__(self, entry):
        # entry == conn.retr()
        super().__init__(b'\r\n'.join(entry[1]))


list_response_pattern = re.compile(rb'\((?P<flags>.*?)\) "(?P<delimiter>.*)" (?P<name>.*)')


def parse_list_response(line):
    flags, delimiter, mailbox_name = list_response_pattern.match(line).groups()
    mailbox_name = mailbox_name.strip(b'"')
    return (flags.decode('utf-8'), delimiter.decode('utf-8'), mailbox_name.decode('utf-8'))
