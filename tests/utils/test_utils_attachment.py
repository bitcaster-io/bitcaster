from datetime import datetime
from typing import Callable

import freezegun
import pytest
from constance.test.pytest import override_config
from django.core.files.uploadedfile import SimpleUploadedFile
from testutils.factories import AttachmentFactory

from bitcaster.exceptions import DownloadKeyDecryptionError, DownloadKeyExpiredError
from bitcaster.models.attachment import Attachment
from bitcaster.utils.attachment import DownloadKeyManager


@pytest.fixture
def attachment() -> Callable[..., Attachment]:
    def _make(**kwargs):
        attached_file = SimpleUploadedFile("test.txt", content=b"TEST")
        return AttachmentFactory(document=attached_file, **kwargs)

    return _make


class TestDownloadKeyManager:
    @override_config(ATTACHMENT_DOWNLOAD_KEY_SALT="testsalt")
    @freezegun.freeze_time(datetime(2025, 1, 1))
    @pytest.mark.parametrize(
        "expires_at", [pytest.param(None, id="perpetual"), pytest.param(datetime(2026, 1, 1), id="fixed-time")]
    )
    def test_fetches_correct_attachment_from_generated_key(self, expires_at, attachment):
        attachment = attachment(correlation_id="getme")
        manager = DownloadKeyManager()
        key = manager.generate_key(attachment, expires_at)
        assert manager.get_attachment(key) == attachment

    @override_config(ATTACHMENT_DOWNLOAD_KEY_SALT="testsalt")
    def test_raises_with_invalid_key(self):
        with pytest.raises(DownloadKeyDecryptionError):
            DownloadKeyManager().get_attachment("thismustfail")

    @override_config(ATTACHMENT_DOWNLOAD_KEY_SALT="testsalt")
    @freezegun.freeze_time(datetime(2025, 1, 1))
    def test_raises_with_expired_key(self, attachment):
        attachment = attachment(correlation_id="getme")
        manager = DownloadKeyManager()
        always_valid_key = manager.generate_key(attachment=attachment, expires_at=None)
        expired_key = manager.generate_key(attachment=attachment, expires_at=datetime(2024, 1, 1))
        assert manager.get_attachment(key=always_valid_key) == attachment, "key should be always valid"
        with pytest.raises(DownloadKeyExpiredError):
            manager.get_attachment(key=expired_key)
