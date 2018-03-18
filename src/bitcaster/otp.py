# -*- coding: utf-8 -*-
import logging

import pyotp

from bitcaster.config.environ import env

logger = logging.getLogger(__name__)


class TOTP(pyotp.TOTP):

    def verify(self, otp, for_time=None, valid_window=0):
        if env('FAKE_OTP'):
            return True
        return super().verify(otp, for_time, valid_window)


totp = TOTP('base32secret3232', interval=1)
