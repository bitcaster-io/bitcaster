import json
import logging
from typing import TYPE_CHECKING, Any, TypedDict

from django.core.signing import Signer
from pywebpush import WebPushException, webpush

from bitcaster.exceptions import DispatcherError

if TYPE_CHECKING:
    from bitcaster.models import Assignment

    SignatureT = TypedDict("SignatureT", {"pk": int, "address": str})  # noqa: UP013


logger = logging.getLogger(__name__)


def sign(assignment: "Assignment") -> str:
    signer = Signer()
    return signer.sign_object({"pk": assignment.pk, "address": assignment.address.value})


def unsign(secret: str) -> "SignatureT":
    signer = Signer()
    data: SignatureT = signer.unsign_object(secret)
    return data


def webpush_send_message(assignment: "Assignment", message: str, **kwargs: Any) -> dict[str, Any]:
    subscription: dict[str, str] = assignment.data["webpush"]["subscription"]
    cfg: "dict[str,str]" = assignment.channel.config

    subscription_info = {"endpoint": subscription["endpoint"], "keys": subscription["keys"]}
    results: dict[str, Any] = {"results": []}
    try:
        webpush(
            subscription_info=subscription_info,
            data=message,
            vapid_private_key=cfg["private_key"],
            vapid_claims=json.loads(cfg["CLAIMS"]),
            verbose=True,
            **kwargs,
        )
        results["success"] = 1
        return results
    except WebPushException as e:
        logger.exception(e)
        raise DispatcherError(e.message) from e
