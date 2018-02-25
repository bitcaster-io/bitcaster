# -*- coding: utf-8 -*-
from logging import getLogger  # noqa

from raven.contrib.django.raven_compat.handlers import SentryHandler

import mercury.env

secLog = getLogger('mercury.security')


class MercuryHandler(SentryHandler):
    def _emit(self, record):
        record.state = mercury.env.env.data
        return super()._emit(record)
