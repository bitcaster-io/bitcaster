import imaplib
import logging

from ..registry import agent_registry
from .email import EmailAbstractOptions, EmailAgent

logger = logging.getLogger(__name__)


class GMailOptions(EmailAbstractOptions):
    pass


@agent_registry.register
class GMailAgent(EmailAgent):
    options_class = GMailOptions

    def _get_connection(self) -> object:
        config = self.config
        imap = imaplib.IMAP4_SSL(host='imap.gmail.com', port=993)
        imap.login(config['username'], config['password'])
        return imap

    def get_usage(self, config):
        return 'https://support.google.com/accounts/answer/185833'
