# -*- coding: utf-8 -*-
from threading import local


class State(local):
    request = None
    data = {}

    def clear(self):
        self.data = {}
        self.request = None


def get_current_user():
    return state.request.user


state = State()
