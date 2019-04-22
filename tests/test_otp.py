import time
from unittest.mock import patch

import pytest

from bitcaster.otp import OtpHandler


def test_otp_handler(settings):
    settings.SECRET_KEY = '1' * 40
    message = 'A really secret message. Not for prying eyes.'

    otp_handler = OtpHandler()

    encrypted = otp_handler.get_otp(message)
    assert encrypted != message
    assert type(encrypted) == bytes

    msg, dt = otp_handler.validate(encrypted)
    assert msg[0] == message

    dt1 = time.time()
    with patch('time.time') as mock:
        mock.return_value = dt1 + 2000  # 2 seconds
        with pytest.raises(ValueError, match='Expired'):
            msg, dt = otp_handler.validate(encrypted, 1)
