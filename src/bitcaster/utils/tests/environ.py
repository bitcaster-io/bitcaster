import os
from contextlib import ContextDecorator
from copy import copy

from bitcaster.config.environ import env


class override_environ(ContextDecorator):
    def __init__(self, *remove, **update):
        self._env = copy(env)
        self.environ = os.environ
        self.update = update or {}
        self.remove = remove or []

        stomped = (set(self.update.keys()) | set(self.remove)) & set(self.environ.keys())
        self.update_after = {k: self.environ[k] for k in stomped}
        self.remove_after = frozenset(k for k in self.update if k not in self.environ)

    def __enter__(self):
        self.environ.update(self.update)
        for k, v in self.update.items():
            env.scheme[k] = (str, v)
        [self.environ.pop(k, None) for k in self.remove]

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.environ.update(self.update_after)
        [self.environ.pop(k) for k in self.remove_after]
