# -*- coding: utf-8 -*-
from django.core.cache import cache


def _get_new_email_key(user):
    return f'new-email-{user.pk}'


def get_new_email_request(user):
    return cache.get(_get_new_email_key(user))


def set_new_email_request(user, email):
    cache.set(_get_new_email_key(user), email)


def clear_new_email_request(user):
    cache.delete(_get_new_email_key(user))
