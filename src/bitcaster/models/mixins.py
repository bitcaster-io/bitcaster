import reversion
from django.db import models
from django.db.models.base import ModelBase
from django.urls import NoReverseMatch, reverse

from bitcaster.utils.language import get_attr


class ReverseWrapper:
    def __init__(self, instance):
        self.__instance = instance
        self.__options = instance.Reverse
        self.__cache = {}

    def __getattr__(self, item):
        name = item.replace('_', '-')
        if item not in self.__cache:
            url = self.__options.pattern.format(op=name)
            args = self.__options.args
            try:
                values = [get_attr(self.__instance, attr) for attr in args]
                self.__cache[name] = reverse(url, args=values)
            except NoReverseMatch:
                self.__cache[name] = reverse(url)

        return self.__cache[name]

    def __repr__(self):
        return repr(self.__options)


class Reverse:
    args = None
    pattern = None
    urls = {}

    def __init__(self, parent):
        if parent:
            for a in ['args', 'pattern']:
                setattr(self, a, getattr(parent, a))

    def __repr__(self):
        return '{} {}'.format(self.pattern, repr(self.args))


class Reverseable(ModelBase):
    def __new__(cls, name, bases, attrs, **kwargs):
        super_new = super().__new__
        attrs['Reverse'] = Reverse(attrs.get('Reverse', None))
        new_class = super_new(cls, name, bases, attrs, **kwargs)
        return new_class


class ReverseWrapperMixin(models.Model, metaclass=Reverseable):

    @property
    def urls(self):
        return ReverseWrapper(self)

    class Meta:
        abstract = True


class ReversionMixin(models.Model):
    class Meta:
        abstract = True

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        with reversion.create_revision():
            super().save(force_insert, force_update, using, update_fields)


#
# class LogMixin:
#     @classmethod
#     def log(cls, **kwargs):
#         request = kwargs.pop('request', state.request)
#         # kwargs.setdefault('application', event.application)
#         # kwargs.setdefault('organization', event.application.organization)
#         # kwargs.setdefault('origin', get_client_ip(request))
#
#         obj = cls.objects.create(**kwargs)
#         stats.occurence.log(event)
#         stats.occurence.log(event.application)
#         stats.occurence.log(event.application.organization)
#         return obj

#
# class RegisterErrorMixin:
#
#     def get_errors(self, granularity='d'):
#         pass
#         # ret = counters.error.get_data(self, granularity=granularity)
#         # return ret[0][1]
#
#     def register_error(self, message, **kwargs):
#         from .error import ErrorEntry
#
#         ErrorEntry.objects.create(message=message,
#                                   application=None,
#                                   target=self,
#                                   data=kwargs).consolidate()
#         # stats.error.log(self)
#         # counters.error.log(self)
#
#
# class StatLogger:
#     def __get__(self, instance, owner):
#         self.instance = instance
#         self.ts = get_timeseries(instance.__class__.__name__)
#         return self
#
#     def __init__(self, metrics: [str] = None) -> None:
#         self.metrics = metrics
#         self.key = 'stats'
#         super().__init__()
#
#     # def contribute_to_class(self, model, name):
#     #     self.model = model
#     #     self.instance = None
#     #     self.ts = get_timeseries(model.__name__)
#     #     self.key = 'stats'
#     #     setattr(model, name, self)
#
#     def get_key(self, metric):
#         if metric:
#             return "%s:%s" % (self.key, metric)
#         return self.key
#
#     def incr(self, metric=None, value=1):
#         self.ts.increase(key=self.get_key(metric), amount=value)
#
#     def decr(self, metric=None, value=1):
#         self.ts.decrease(key=self.get_key(metric), amount=value)
#
#     def set(self, metric=None, value=1):
#         self.ts.set(key=self.get_key(metric), amount=value)
#
#     def get_data(self, metric=None, granularity='h', count=None):
#         if count is None:
#             props = self.ts.granularities[granularity]
#             count = props['ttl'] // props['duration']
#         return self.ts.get_buckets(key=self.get_key(metric),
#                                    granularity=granularity,
#                                    count=count)
#
#
# class QueueLogger:
#     def contribute_to_class(self, model, name):
#         self.model = model
#         self.ts = get_timeseries(model.__name__)
#         self.key = 'queue'
#         setattr(model, name, self)
#
#     def incr(self, value=1, obj=None):
#         self.ts.increase(key=self.key, amount=value)
#
#     def decr(self, value=1, obj=None):
#         self.ts.decrease(key=self.key, amount=value)
#
#     def set(self, value=1, obj=None):
#         self.ts.set(key=self.key, amount=value)
#
#     def get_data(self, granularity='h', count=None):
#         if count is None:
#             props = self.ts.granularities[granularity]
#             count = props['ttl'] // props['duration']
#         return self.ts.get_buckets(key=self.key,
#                                    granularity=granularity,
#                                    count=count)
