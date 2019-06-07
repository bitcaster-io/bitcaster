from django.core.cache import caches

lock = caches['lock']


def get_all_locks():
    return {i: key for i, key in enumerate(lock.keys('*'))}
