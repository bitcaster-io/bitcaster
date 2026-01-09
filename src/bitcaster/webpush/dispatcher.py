import base64
import json
import logging
from typing import TYPE_CHECKING, Any

import ecdsa
from django import forms
from django.utils.translation import gettext_lazy as _
from py_vapid import Vapid02

from bitcaster.dispatchers.base import (
    Dispatcher,
    DispatcherConfig,
    MessageProtocol,
    Payload,
)
from bitcaster.exceptions import DispatcherError
from bitcaster.state import state

if TYPE_CHECKING:
    from bitcaster.models import Assignment

logger = logging.getLogger(__name__)


class TokenInput(forms.HiddenInput):
    pass


def generate_vapid_keypair():
    pk = ecdsa.SigningKey.generate(curve=ecdsa.NIST256p)
    vk = pk.get_verifying_key()
    return {
        "private_key": base64.urlsafe_b64encode(pk.to_string()).strip(b"="),
        "public_key": base64.urlsafe_b64encode(b"\x04" + vk.to_string()).strip(b"="),
    }


class WebPushConfig(DispatcherConfig):
    help_text = """

1. goto [Firebase Console](https://console.firebase.google.com/u/0/?pli=1){:target="_blank"} and create a new project
2. After creation, navigate to 'Project Settings'
3. Goto 'Cloud Messaging' tab'
3. Get the 'Sender ID' value and inert it in the
4. Scroll down to the 'Web configuration' section and click 'Generate key pair'.
5. Copy the Private Key and insert it here

Notes:
- [https://web.dev/articles/push-notifications-web-push-protocol](#)

    """
    application_id = forms.CharField(
        label=_("Sender ID"), help_text=_("Firebase Cloud Messaging API (V1) Sender ID"), required=True
    )
    private_key = forms.CharField(label=_("Private Key"), help_text=_("private key"), required=True)
    email = forms.EmailField(label=_("Claim Email Key"), help_text=_("JWT contact information"))

    APPLICATION_SERVER_KEY = forms.CharField(widget=TokenInput, required=False)
    VAPID = forms.CharField(widget=TokenInput, required=False)
    CLAIMS = forms.CharField(widget=TokenInput, required=False)

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        initial = kwargs.pop("initial", {})
        if "email" not in initial:
            initial["email"] = state.request.user.email
        super().__init__(*args, initial=initial, **kwargs)

    def clean(self) -> dict[str, Any] | None:
        super().clean()
        if "email" in self.cleaned_data:
            keys = generate_vapid_keypair()
            private_key = self.cleaned_data.get("private_key")
            vapid = Vapid02.from_string(private_key)
            claims = {"sub": "mailto: %s" % self.cleaned_data["email"], "aud": "https://android.googleapis.com"}
            auth = vapid.sign(claims)
            self.cleaned_data["APPLICATION_SERVER_KEY"] = keys["public_key"]
            self.cleaned_data["VAPID"] = auth["Authorization"]
            self.cleaned_data["CLAIMS"] = json.dumps(claims)

        return self.cleaned_data


class WebPushDispatcher(Dispatcher):
    config_class: type[DispatcherConfig] = WebPushConfig
    protocol = MessageProtocol.WEBPUSH
    need_subscription = True

    def send(self, address: str, payload: Payload, assignment: "Assignment | None" = None, **kwargs: Any) -> bool:
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
            raise DispatcherError(e) from e
