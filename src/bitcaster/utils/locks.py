from django.core.cache import caches

lock = caches['lock']


def get_all_locks(filter='*'):
    return {i: key for i, key in enumerate(lock.keys(filter))}
