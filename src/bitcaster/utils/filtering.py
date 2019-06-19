import logging
import operator
from functools import reduce

from django.db.models import Q
from django.utils.functional import cached_property
from django.utils.translation import gettext as _

logger = logging.getLogger(__name__)


class FilterParser:
    def __init__(self, view, mapping, search_fields=None):
        self.view = view
        self._mapping = mapping
        self.search_fields = search_fields or mapping.keys()
        self.errors = []

    @cached_property
    def mapping(self):
        return {str(k): v for k, v in self._mapping.items()}

    def _parse_field(self, token):
        try:
            field_name, value = token.split(':')
            rule = self.mapping.get(field_name)
            handler = getattr(self.view, str(rule), None)
            if callable(rule):
                rule(self, field_name, value)
            elif callable(handler):
                handler(self, field_name, value)
            elif isinstance(rule, str):
                self.kwargs[rule] = value.strip()
            elif callable(rule):
                rule(self)
            else:
                self.errors.append(_('unknown field %(field_name)s') % dict(field_name=field_name))
        except Exception as e:
            self.errors.append(str(e))
            logger.exception(e)

    def parse(self, string: str):
        if not string:
            return [], {}, []
        self.args = [Q()]
        self.kwargs = {}
        self.errors = []
        # _aa = [Q()]
        # ret = {}
        words = []
        string = string.lower().replace(': ', ':').replace(' :', ':')
        tokens = string.lower().split()
        for token in tokens:
            if ':' in token:
                self._parse_field(token)
            else:
                words.append(token)
        for w in words:
            for f in self.search_fields:
                if isinstance(f, str):
                    self.args.append(Q(**{f: w}))
        self.args = reduce(operator.or_, self.args)

        return self.args, self.kwargs, self.errors
