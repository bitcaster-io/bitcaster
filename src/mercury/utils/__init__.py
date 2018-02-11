# -*- coding: utf-8 -*-
from __future__ import absolute_import

from .reflect import fqn, import_by_name  # noqa

# from .language import get_attr, reraise_as # noqa


# def sane_repr(*attrs):
#     if 'id' not in attrs and 'pk' not in attrs:
#         attrs = ('id',) + attrs
#
#     def _repr(self):
#         cls = type(self).__name__
#         pairs = ('%s=%s' % (a, repr(getattr(self, a, None))) for a in attrs)
#         return u'<%s at 0x%x: %s>' % (cls, id(self), ', '.join(pairs))
#
#     return _repr
