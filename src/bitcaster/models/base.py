import logging

from concurrency.fields import IntegerVersionField
from django.db import models

logger = logging.getLogger(__name__)


# def sane_repr(*attrs):
#     if 'id' not in attrs and 'pk' not in attrs:
#         attrs = ('id',) + attrs
#
#     def _repr(self):
#         cls = type(self).__name__
#
#         pairs = (
#             '%s=%s' % (a, repr(getattr(self, a, None)))
#             for a in attrs)
#
#         return u'<%s at 0x%x: %s>' % (cls, id(self), ', '.join(pairs))
#
#     return _repr


class AbstractModel(models.Model):
    version = IntegerVersionField()
    last_modify_date = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        app_label = 'bitcaster'
