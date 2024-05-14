from typing import TYPE_CHECKING

import pytest

from bitcaster.exceptions import DispatcherError
from bitcaster.webpush.utils import sign, unsign, webpush_send_message

if TYPE_CHECKING:
    from bitcaster.models import Assignment


def test_webpush_send_message(mocked_responses, push_assignment, fcm_url):
    mocked_responses.add(mocked_responses.POST, fcm_url)
    webpush_send_message(push_assignment, "===")

    mocked_responses.add(mocked_responses.POST, fcm_url, "Error", status=400)
    with pytest.raises(DispatcherError):
        webpush_send_message(push_assignment, "===")


def test_sign(push_assignment: "Assignment"):
    assert unsign(sign(push_assignment))
