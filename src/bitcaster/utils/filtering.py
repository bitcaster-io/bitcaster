import operator
from functools import reduce

from django.db.models import Q


class FilterParser:
    def __init__(self, view, mapping):
        self.view = view
        self.mapping = mapping

    def _parse_field(self, token):
        try:
            kw, value = token.split(':')
            rule = self.mapping.get(kw)
            handler = getattr(self.view, rule, None)
            if callable(handler):
                handler(self, kw, value)
            elif isinstance(rule, str):
                self.kwargs[rule] = value.strip()
            elif callable(rule):
                rule(self)
        except Exception:
            pass

    def parse(self, string: str):
        if not string:
            return [], {}
        self.args = [Q()]
        self.kwargs = {}
        # _aa = [Q()]
        # ret = {}
        words = []

        tokens = string.lower().split()
        for token in tokens:
            if ':' in token:
                self._parse_field(token)
            else:
                words.append(token)
        for w in words:
            for f in self.mapping.values():
                if isinstance(f, str):
                    self.args.append(Q(**{f: w}))
        self.args = reduce(operator.or_, self.args)

        return self.args, self.kwargs
