from django.db.models.base import ModelBase
from django.urls import reverse

from bitcaster.utils.language import get_attr


class ReverseWrapper:
    def __init__(self, instance):
        self.__instance = instance
        self.__options = instance.Reverse

    def __getattr__(self, item):
        url = self.__options.pattern.format(op=item)
        args = self.__options.args
        if item in self.__options.actions:
            return reverse(url,
                           args=[get_attr(self.__instance, attr) for attr in args])
        elif item in self.__options.links:
            return reverse(url)
        return '404'

    def __repr__(self):
        return repr(self.__options)


class Reverse:
    args = ['organization.slug']
    pattern = 'org-{op}'
    actions = ['edit', 'delete', 'dashboard']
    links = ['create', 'list']

    def __init__(self, other):
        if other:
            for a in ['args', 'pattern', 'actions', 'links']:
                if hasattr(other, a):
                    setattr(self, a, getattr(other, a))

    def __repr__(self):
        return repr(self.actions + self.links)


class PIPPO(ModelBase):
    def __new__(cls, name, bases, attrs, **kwargs):
        super_new = super().__new__
        attrs['Reverse'] = Reverse(attrs.get('Reverse', None))
        new_class = super_new(cls, name, bases, attrs, **kwargs)
        return new_class


class ReverseWrapperMixin(metaclass=PIPPO):

    @property
    def urls(self):
        return ReverseWrapper(self)
