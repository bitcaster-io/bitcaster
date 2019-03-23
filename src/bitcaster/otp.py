# -*- coding: utf-8 -*-
import base64
import logging
import random
import re
import string
import time

import pyotp
import six
from cryptography.fernet import Fernet
from django.conf import settings

from bitcaster.config.environ import env

logger = logging.getLogger(__name__)


class TOTP(pyotp.TOTP):

    def verify(self, otp, for_time=None, valid_window=0):
        if env('FAKE_OTP'):
            return True
        return super().verify(otp, for_time, valid_window)


totp = TOTP('base32secret3232', interval=1)


class OtpHandler:
    def __init__(self, separator='|') -> None:
        super().__init__()
        self.separator = separator
        # Fernet key must be 32 url-safe base64-encoded byte
        self.encryption_suite = Fernet(base64.urlsafe_b64encode(settings.SECRET_KEY.encode()[:32]))

    def get_otp(self, message_list):
        """
        Generates a url-safe base64 encoded encypted message together with current timestamp (to the second).
        Throws in some random number of characters to prenvent ecryption chill exploit
        Args:
            message_list: the message to be encrypted

        Returns:

        """
        if isinstance(message_list, six.string_types):
            message_list = [message_list, ]
        for x in message_list:
            if self.separator in x:
                raise ValueError('Messages cannot contain separator')
        message_list = self.separator.join(message_list)
        dt = int(time.time())
        prefix = ''.join([random.choice(string.ascii_letters) for x in range(random.randint(0, 20))])
        tail = ''.join([random.choice(string.ascii_letters) for x in range(random.randint(0, 20))])
        message_list = f'{message_list}{self.separator}{prefix}{dt}{tail}'
        message_list = self.encryption_suite.encrypt(message_list.encode())
        return base64.urlsafe_b64encode(message_list)

    def validate(self, cipher_text, max_timedelta=None):
        """
        Will decrypt the url safe base64 encoded crypted str or bytes array.
        Args:
            cipher_text: the encrypted text
            max_timedelta: maximum timedelta in seconds

        Returns:
            the original message list
        """
        if isinstance(cipher_text, six.string_types):
            cipher_text.encode()
        cipher_text = base64.urlsafe_b64decode(cipher_text)
        decrypted = self.encryption_suite.decrypt(cipher_text).decode().split(self.separator)
        message_list, dt = decrypted[:-1], decrypted[-1]
        dt = int(''.join(re.findall(r'\d+', dt)))
        now = int(time.time())
        if max_timedelta and max_timedelta < now - dt:
            raise ValueError('Expired')
        return message_list, dt
