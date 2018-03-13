# -*- coding: utf-8 -*-
from threading import local


class State(local):
    request = None
    data = {}

    def clear(self):
        self.data = {}
        self.request = None


state = State()
