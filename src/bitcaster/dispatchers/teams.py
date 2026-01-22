import logging
from typing import TYPE_CHECKING, Any

import requests
from django import forms
from django.utils.translation import gettext_lazy as _

from bitcaster.dispatchers.base import Dispatcher, DispatcherConfig, MessageProtocol, Payload
from bitcaster.exceptions import DispatcherError

if TYPE_CHECKING:
    from bitcaster.models import Assignment

logger = logging.getLogger(__name__)


class TeamsConfig(DispatcherConfig):
    webhook_url = forms.URLField(
        label=_("Webhook URL"), help_text=_("The Incoming Webhook URL from Microsoft Teams channel configuration.")
    )


class TeamsDispatcher(Dispatcher):
    slug = "teams"
    verbose_name = "Microsoft Teams"
    protocol = MessageProtocol.MARKDOWN
    config_class = TeamsConfig

    def _get_connection(self) -> requests.Session:
        return requests.Session()

    def send(self, address: str, payload: Payload, assignment: "Assignment | None" = None, **kwargs: Any) -> bool:
        webhook_url = self.channel.config.get("webhook_url")

        if not webhook_url:
            raise DispatcherError("Webhook URL not configured for this channel")
        text_content = payload.message

        # Adaptive Card Payload
        teams_message = {
            "type": "message",
            "attachments": [
                {
                    "contentType": "application/vnd.microsoft.card.adaptive",
                    "contentUrl": None,
                    "content": {
                        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                        "type": "AdaptiveCard",
                        "version": "1.4",
                        "body": [
                            {
                                "type": "TextBlock",
                                "text": payload.subject,
                                "weight": "Bolder",
                                "size": "Medium",
                                "wrap": True,
                            },
                            {
                                "type": "TextBlock",
                                "text": "Bitcaster Notification",
                                "isSubtle": True,
                                "spacing": "None",
                                "size": "Small",
                            },
                            {"type": "TextBlock", "text": text_content, "wrap": True, "spacing": "Medium"},
                        ],
                    },
                }
            ],
        }

        try:
            session = self._get_connection()
            response = session.post(webhook_url, json=teams_message, timeout=10)

            if response.status_code != 200:
                logger.error(f"Teams dispatcher error: {response.status_code} - {response.text}")
                raise DispatcherError(f"Failed to send to Teams: {response.text}")

            return True

        except requests.RequestException as e:
            logger.exception("Network error sending to Teams")
            raise DispatcherError(f"Network error: {e}") from e

    def test_connection(self, raise_exception: bool = False) -> bool:
        if not self.channel.config.get("webhook_url"):
            if raise_exception:
                raise DispatcherError("Webhook URL missing")
            return False
        return True
