# -*- coding: utf-8 -*-
from logging import getLogger  # noqa

from raven.contrib.django.raven_compat.handlers import SentryHandler

import bitcaster.state

secLog = getLogger('bitcaster.security')


class BitcasterHandler(SentryHandler):
    def _emit(self, record):
        record.state = bitcaster.state.state.data
        return super()._emit(record)
