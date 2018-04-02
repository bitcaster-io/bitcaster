# -*- coding: utf-8 -*-
from constance import config
from django.conf import settings
from django.shortcuts import resolve_url
from django.utils import timezone
from django.utils.encoding import force_text
from django.utils.functional import Promise
from social_django.strategy import DjangoStrategy

from bitcaster.models import OrganizationMember, User

# from social_core.pipeline.user import create_user


# def associate(backend, details, user=None, *args, **kwargs):
#     return None


USER_FIELDS = ['username', 'email', 'fullname']


def associate_invitation(backend, details, user=None, strategy=None, *args, **kwargs):
    invitation_id = strategy.session_get('invitation')
    is_new = False
    if invitation_id:
        invite = OrganizationMember.objects.get(pk=invitation_id, user__isnull=True)
        # if not user:
        is_new = True
        fields = {"email": details['email'],
                  "name": details['fullname'],
                  "friendly_name": details['username']}
        user = User.objects.create(**fields)
        invite.user = user
        invite.date_enrolled = timezone.now()
        invite.save()

    return {
        'is_new': is_new,
        'user': user
    }


# def avatar(backend, details, user=None, *args, **kwargs):
#     is_new = kwargs.get('is_new', False)
#     if is_new:
#         pass
#
#     return False


class BitcasterStrategy(DjangoStrategy):
    def get_setting(self, name):
        "get configuration from 'constance.config' first "
        value = getattr(config, name, None)
        if value is None:
            value = getattr(settings, name)
        # Force text on URL named settings that are instance of Promise
        if name.endswith('_URL'):
            if isinstance(value, Promise):
                value = force_text(value)
            value = resolve_url(value)
        return value
