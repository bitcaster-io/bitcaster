# -*- coding: utf-8 -*-
from threading import local


class State(local):
    request = None
    data = {}
    debug = {}

    def clear(self):
        self.data = {}
        self.request = None


def get_current_user():
    if state.request and state.request.user.is_authenticated:
        return state.request.user


state = State()
