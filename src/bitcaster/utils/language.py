from django.utils.translation import gettext_lazy as _


class Dummy(object):
    pass


def parse_bool(value):
    return value.lower() in ['1', 'true', 'yes', 'y', 't', _('true'), _('yes')]
    # return value.lower() not in ['', '0', 'false', 'f', 'n']


def flatten(x):
    """flatten(sequence) -> list

    Returns a single, flat list which contains all elements retrieved
    from the sequence and all recursively contained sub-sequences
    (iterables).

    Examples:

    >>> [1, 2, [3,4], (5,6)]
    [1, 2, [3, 4], (5, 6)]

    >>> flatten([[[1,2,3], (42,None)], [4,5], [6], 7, (8,9,10)])
    [1, 2, 3, 42, None, 4, 5, 6, 7, 8, 9, 10]"""

    result = []
    for el in x:
        # if isinstance(el, (list, tuple)):
        if hasattr(el, '__iter__') and not isinstance(el, str):
            result.extend(flatten(el))
        else:
            result.append(el)
    return list(result)


def get_attr(obj, attr, default=None):
    """Recursive get object's attribute. May use dot notation.

    >>> class C(object): pass
    >>> a = C()
    >>> a.b = C()
    >>> a.b.c = 4
    >>> get_attr(a, 'b.c')
    4

    >>> get_attr(a, 'b.c.y', None)

    >>> get_attr(a, 'b.c.y', 1)
    1
    """
    if '.' not in attr:
        return getattr(obj, attr, default)
    else:
        L = attr.split('.')
        return get_attr(getattr(obj, L[0], default), '.'.join(L[1:]), default)


class classproperty(object):
    def __init__(self, getter):
        self.getter = getter

    def __get__(self, instance, owner):
        return self.getter(owner)


def repr_list(iterable):
    return ', '.join("'%s'" % str(i) for i in iterable)
