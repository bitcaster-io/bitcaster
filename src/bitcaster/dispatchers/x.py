from typing import TYPE_CHECKING, Any

import logging

from requests_oauthlib import OAuth1Session

from django import forms
from django.utils.translation import gettext_lazy as _

from .base import Dispatcher, DispatcherConfig, MessageProtocol, Payload
from ..exceptions import DispatcherError

if TYPE_CHECKING:
    from ..models import Assignment

logger = logging.getLogger(__name__)


class XConfig(DispatcherConfig):
    consumer_key = forms.CharField(label=_("Consumer Key"))
    consumer_key_secret = forms.CharField(label=_("Consumer Key Secret"))
    access_token = forms.CharField(label=_("Access Token"))
    access_token_secret = forms.CharField(label=_("Access Token Secret"))


class XDispatcher(Dispatcher):
    id = 500
    slug = "x"
    verbose_name = "X (Twitter)"
    config_class = XConfig
    protocol = MessageProtocol.PLAINTEXT

    MAX_CHARS = 280

    def _send(self, address: str, payload: Payload, assignment: "Assignment | None" = None, **kwargs: Any) -> bool:
        text = payload.message[: self.MAX_CHARS]

        session = OAuth1Session(
            client_key=self.config["consumer_key"],
            client_secret=self.config["consumer_key_secret"],
            resource_owner_key=self.config["access_token"],
            resource_owner_secret=self.config["access_token_secret"],
        )
        response = session.post("https://api.twitter.com/2/tweets", json={"text": text})

        if response.status_code not in (200, 201):
            logger.error(f"X dispatcher error: {response.status_code} - {response.text}")
            raise DispatcherError(f"Failed to post to X: {response.text}")

        return True

    def get_extra_config_info(self) -> str:
        return (
            "Messages are truncated to 280 characters. "
            'Go to your App\'s <a href="https://developer.x.com" target="_blank">Keys &amp; Tokens</a> page, '
            "copy the Consumer Key and Consumer Key Secret from <strong>OAuth 1.0 Keys</strong>, "
            "then click <strong>Show</strong> on the Access Token to reveal the "
            "Access Token and Access Token Secret. "
            "Ensure the token has <strong>Read and Write</strong> permissions "
            'under "User authentication settings".'
        )
