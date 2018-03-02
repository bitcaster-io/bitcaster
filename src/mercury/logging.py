# -*- coding: utf-8 -*-
from logging import getLogger  # noqa

from raven.contrib.django.raven_compat.handlers import SentryHandler

import mercury.state

secLog = getLogger('mercury.security')


class MercuryHandler(SentryHandler):
    def _emit(self, record):
        record.state = mercury.state.state.data
        return super()._emit(record)
