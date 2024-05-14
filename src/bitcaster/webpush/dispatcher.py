import json
import logging
from typing import Any, Optional

from cryptography.hazmat.primitives import serialization
from django import forms
from django.utils.translation import gettext as _
from py_vapid import Vapid02, b64urlencode

from bitcaster.dispatchers.base import (
    Dispatcher,
    DispatcherConfig,
    MessageProtocol,
    Payload,
)
from bitcaster.exceptions import DispatcherError
from bitcaster.models import Assignment

logger = logging.getLogger(__name__)


def clean_key(value: str) -> str:
    return value.replace("\n", "").replace("-----BEGIN PRIVATE KEY-----", "").replace("-----END PRIVATE KEY-----", "")


class TokenInput(forms.TextInput):
    pass


class WebPushConfig(DispatcherConfig):
    application_id = forms.CharField(label=_("Sender ID"), help_text=_("Sender ID"), required=False)
    private_key = forms.CharField(label=_("Private Key"), help_text=_("private key"), required=False)
    email = forms.EmailField(label=_("Claim Email Key"), help_text=_("JWT contact information"))

    APPLICATION_SERVER_KEY = forms.CharField(widget=TokenInput, required=False)
    VAPID = forms.CharField(widget=TokenInput, required=False)
    CLAIMS = forms.CharField(widget=TokenInput, required=False)

    def clean(self) -> dict[str, Any] | None:
        super().clean()
        if "email" in self.cleaned_data:
            vapid = Vapid02()
            vapid.generate_keys()
            if not (private_key := self.cleaned_data.get("private_key")):
                private_key = clean_key(vapid.private_pem().decode())
            vapid = Vapid02.from_string(private_key)
            raw_pub = vapid.public_key.public_bytes(
                serialization.Encoding.X962, serialization.PublicFormat.UncompressedPoint
            )
            claims = {"sub": "mailto: %s" % self.cleaned_data["email"], "aud": "https://android.googleapis.com"}
            auth = vapid.sign(claims)
            self.cleaned_data["APPLICATION_SERVER_KEY"] = b64urlencode(raw_pub)
            self.cleaned_data["VAPID"] = auth["Authorization"]
            self.cleaned_data["CLAIMS"] = json.dumps(claims)

        return self.cleaned_data


class WebPushDispatcher(Dispatcher):

    help_text = """

1. goto [Firebase Console](https://console.firebase.google.com/u/0/?pli=1){:target="_blank"} and create a new project
2. After creation navigate to 'Project Settings'
3. Under 'Cloud Messaging' tab in the 'Web configuration' section click on 'Generate key pair'
4. Copy the Private Key and insert here

Note: [https://web.dev/articles/push-notifications-web-push-protocol](#)

"""

    config_class: type[DispatcherConfig] = WebPushConfig
    protocol = MessageProtocol.WEBPUSH
    need_subscription = True

    def send(self, address: str, payload: Payload, assignment: "Optional[Assignment]" = None, **kwargs: Any) -> bool:
        try:
            from .utils import webpush_send_message

            if not assignment:
                raise ValueError(_("WebPushDispatcher: assignment arg must be provided"))

            if not assignment.data:
                raise DispatcherError(_("Assignment not subscribed"))
            msg = json.dumps({"message": payload.message, "subject": payload.subject})
            res: dict[str, Any] = webpush_send_message(message=msg, assignment=assignment, **kwargs)
            return res["success"] == 1
        except Exception as e:
            logger.exception(e)
            raise DispatcherError(e)
