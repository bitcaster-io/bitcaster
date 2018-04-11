# -*- coding: utf-8 -*-
import os


class environment:
    """
    Helper for setting environmental variables, merges. Usages:
    with environment({'HTTPS': 'off'}):
       pass
    """
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def __enter__(self):
        from bitcaster.config.environ import env
        self.old1 = os.environ
        self.old2 = env.ENVIRON
        os.environ = dict(os.environ, **self.kwargs)
        env.ENVIRON = dict(env.ENVIRON, **self.kwargs)

    def __exit__(self, type, value, traceback):
        from bitcaster.config.environ import env
        os.environ = self.old1
        env.ENVIRON = self.old2
