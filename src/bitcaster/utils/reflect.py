import types
from inspect import isclass

from strategy_field.utils import import_by_name  # noqa


def fqn(o):
    """Returns the fully qualified class name of an object or a class

    :param o: object or class
    :return: class name
    """
    parts = []
    if isinstance(o, (str, bytes)):
        return o
    if not hasattr(o, '__module__'):
        raise ValueError('Invalid argument `%s`' % o)
    parts.append(o.__module__)
    if isclass(o):
        parts.append(o.__name__)
    elif isinstance(o, types.FunctionType):
        parts.append(o.__name__)
    else:
        parts.append(o.__class__.__name__)
    return '.'.join(parts)


def package_name(c):
    return fqn(c).split('.')[0]
