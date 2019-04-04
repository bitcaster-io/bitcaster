from django.core.cache import cache


def _get_new_email_key(user):
    return f'new-email-{user.pk}'


def check_new_email_address_request(user):
    return cache.get(_get_new_email_key(user))


def set_request_new_email_address(user, email):
    cache.set(_get_new_email_key(user), email)


def clear_new_email_address_request(user):
    cache.delete(_get_new_email_key(user))
