from typing import TYPE_CHECKING, Any

import logging

import requests
from requests import Response

from django import forms
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.translation import gettext_lazy as _

from .base import Dispatcher, DispatcherConfig, MessageProtocol, Payload

if TYPE_CHECKING:
    from ..models import Assignment

logger = logging.getLogger(__name__)

SLACK_ALLOWED_HOSTS = {"hooks.slack.com"}


class SlackConfig(DispatcherConfig):
    url = forms.URLField(label=_("URL"), assume_scheme="https")

    def clean_url(self) -> str:
        url = self.cleaned_data["url"]
        if not url_has_allowed_host_and_scheme(url, allowed_hosts=SLACK_ALLOWED_HOSTS, require_https=True):
            raise DjangoValidationError("URL must be a valid Slack webhook (hooks.slack.com)")
        return url


class SlackDispatcher(Dispatcher):
    id = 500
    slug = "slack"
    config_class: type[DispatcherConfig] = SlackConfig
    protocol = MessageProtocol.PLAINTEXT
    verbose_name = "Slack"

    def _send(self, address: str, payload: Payload, assignment: "Assignment | None" = None, **kwargs: Any) -> bool:
        res: Response = requests.post(self.config["url"], json={"text": payload.message}, timeout=10)
        return res.status_code == 200
