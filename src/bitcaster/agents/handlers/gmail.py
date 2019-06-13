import imaplib
import logging

from ..registry import agent_registry
from .imap import EmailAbstractOptions, ImapAgent

logger = logging.getLogger(__name__)


class GMailOptions(EmailAbstractOptions):
    fieldset_defs = (('Credentials', ('username', 'password')),
                     ('Event', ('event',)),
                     ('Filtering', ('folder', 'unseen',
                                    'subject_regex',
                                    'body_regex',
                                    'sender_regex', 'to_regex')),
                     ('Policy', ('policy', 'processed_folder')),
                     )

    def get_agent(self):
        return GMailAgent


@agent_registry.register
class GMailAgent(ImapAgent):
    options_class = GMailOptions
    icon = 'mail-gmail.png'

    def _get_connection(self, config=None) -> object:  # pragma: no cover
        config = config or self.config
        imap = imaplib.IMAP4_SSL(host='imap.gmail.com', port=993)
        imap.login(config['username'], config['password'])
        return imap

    def get_usage(self):
        return 'https://support.google.com/accounts/answer/185833'
