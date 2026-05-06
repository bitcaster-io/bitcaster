from typing import Callable

from datetime import datetime

from constance.test.pytest import override_config

import freezegun
import pytest
from testutils.factories import AttachmentFactory

from django.core.files.uploadedfile import SimpleUploadedFile

from bitcaster.exceptions import DecryptionError, KeyExpiredError
from bitcaster.models.attachment import Attachment
from bitcaster.utils.security import KeyManager


@pytest.fixture
def attachment() -> Callable[..., Attachment]:
    def _make(**kwargs):
        attached_file = SimpleUploadedFile("test.txt", content=b"TEST")
        return AttachmentFactory(document=attached_file, **kwargs)

    return _make


@override_config(SECRET_KEY_SALT="testsalt")
@freezegun.freeze_time(datetime(2025, 1, 1))
@pytest.mark.parametrize("expires_at", [pytest.param(None, id="perpetual"), pytest.param(10, id="fixed-time")])
def test_fetches_correct_attachment_from_generated_key(expires_at, attachment):
    attachment = attachment(correlation_id="getme")
    manager = KeyManager()
    key = manager.generate_key(expires_at, attachment=attachment.pk)
    parts = manager.parse_key(key)
    assert attachment.pk == parts["attachment"]


@override_config(SECRET_KEY_SALT="testsalt")
def test_raises_with_invalid_key():
    with pytest.raises(DecryptionError):
        KeyManager().parse_key("thismustfail")


@override_config(SECRET_KEY_SALT="testsalt")
def test_raises_with_expired_key(attachment):
    attachment = attachment(correlation_id="getme")
    manager = KeyManager()
    always_valid_key = manager.generate_key(None, attachment=attachment.pk)

    with freezegun.freeze_time(datetime(2025, 1, 1)):
        expired_key = manager.generate_key(10, attachment=attachment.pk)
    assert manager.parse_key(always_valid_key)
    with pytest.raises(KeyExpiredError):
        assert manager.parse_key(expired_key)
