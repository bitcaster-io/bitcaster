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
    args = ['organization.slug']
    pattern = 'org-{op}'

    def __init__(self, other):
        if other:
            for a in ['args', 'pattern']:
                if hasattr(other, a):
                    setattr(self, a, getattr(other, a))

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
