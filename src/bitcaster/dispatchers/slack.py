import logging
from typing import TYPE_CHECKING, Any

import requests
from django import forms
from django.utils.translation import gettext as _
from requests import Response

from ..exceptions import DispatcherError
from .base import Dispatcher, DispatcherConfig, MessageProtocol, Payload

if TYPE_CHECKING:
    from ..models import Assignment

logger = logging.getLogger(__name__)


class SlackConfig(DispatcherConfig):
    url = forms.URLField(label=_("URL"), assume_scheme="https")


class SlackDispatcher(Dispatcher):
    id = 500
    slug = "slack"
    config_class: type[DispatcherConfig] = SlackConfig
    protocol = MessageProtocol.PLAINTEXT

    def send(self, address: str, payload: Payload, assignment: "Assignment | None" = None, **kwargs: Any) -> bool:
        try:
            conn = requests.Session()
            res: Response = conn.post(self.config["url"], json={"text": payload.message})
            return res.status_code == 200
        except Exception as e:
            logger.exception(e)
            raise DispatcherError(e) from e
