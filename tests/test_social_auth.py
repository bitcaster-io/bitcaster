# -*- coding: utf-8 -*-
from unittest.mock import Mock

import pytest
from django.conf import settings
from django.utils.functional import lazystr

from bitcaster.models import OrganizationMember
from bitcaster.social_auth import BitcasterStrategy, associate_invitation


@pytest.mark.django_db
def test_associate_invitation_no_invite():
    ret = associate_invitation(None, {'email': 'test@test.org',
                                      'fullname': 'User',
                                      'username': 'username'
                                      },
                               strategy=Mock(session_get=lambda x: {'invitation': 0}[x]))
    assert not ret['is_new']


@pytest.mark.django_db
def test_associate_invitation_invite(organization1):
    invite = OrganizationMember.objects.create(email='test@test.org', organization=organization1)
    ret = associate_invitation(None, {'email': 'test@test.org',
                                      'fullname': 'User',
                                      'username': 'username'
                                      },
                               strategy=Mock(session_get=lambda x: {'invitation': invite.pk}[x]))
    assert ret['is_new']
    assert ret['user']

    assert organization1.memberships.filter(user=ret['user']).exists()


def test_strategy(monkeypatch):
    strategy = BitcasterStrategy(Mock())
    assert strategy.get_setting('MEDIA_URL') == settings.MEDIA_URL
    assert not strategy.get_setting('INITIALIZED')

    monkeypatch.setattr(settings, 'PROMISE_URL', lazystr('index'), False)
    assert strategy.get_setting('PROMISE_URL') == '/'
