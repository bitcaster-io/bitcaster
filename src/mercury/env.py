# -*- coding: utf-8 -*-
import logging
from threading import local

logger = logging.getLogger(__name__)


class State(local):
    request = None
    data = {}

    def clear(self):
        self.data = {}
        self.request = None


env = State()
