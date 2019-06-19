from django.core.cache import caches

from bitcaster.utils.reflect import fqn

cache = caches['default']


def redis_property(f):
    def _inner(instance):
        key = '%s:%s' % (fqn(instance), instance.pk)
        value = cache.get(key, None)
        if key is None:
            value = f(instance)
        return value

    # _inner.delete = lambda cache.delete(key)
    return _inner
