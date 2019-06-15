from django.core.cache import caches

lock = caches['lock']


def get_all_locks(filter='*'):
    return {i: key for i, key in enumerate(lock.keys(filter))}


def remove_locks(filter):
    for key in lock.keys(filter):
        lock.delete(key)
