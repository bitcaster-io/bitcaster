import logging
from typing import Type

import requests
from django import forms
from django.utils.translation import gettext as _
from requests import Response

from ..exceptions import DispatcherError
from .base import Dispatcher, DispatcherConfig, Payload

logger = logging.getLogger(__name__)


class SlackConfig(DispatcherConfig):
    url = forms.URLField(label=_("URL"))


class SlackDispatcher(Dispatcher):
    id = 500
    slug = "slack"
    config_class: Type[DispatcherConfig] = SlackConfig
    has_subject = False

    def send(self, address: str, payload: Payload) -> "Response":
        try:
            conn = requests.Session()
            res = conn.post(self.config["url"], json={"text": payload.message})
            return res
        except Exception as e:
            logger.exception(e)
            raise DispatcherError(e)
