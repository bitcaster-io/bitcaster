import os
from unittest import mock

import pytest
import pytz
from constance.test import override_config
from django.urls import reverse

from bitcaster.utils.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


def test_user_profile(django_app, organization1, user1):
    # UserProfileView
    url = reverse('user-profile', args=[organization1.slug])
    res = django_app.get(url, user=user1)
    res.form['friendly_name'] = 'Name'
    res.form['timezone'].force_value(pytz.timezone('Europe/Rome'))
    res.form['country'].force_value('IT')
    res = res.form.submit()
    assert res.status_code == 302, f"Submit failed with: {repr(res.context['form'].errors)}"


@override_config(IPSTACK_KEY=os.environ.get('BITCASTER_IPSTACK_KEY'))
@mock.patch('bitcaster.web.views.user.base.get_client_ip', lambda r: '77.242.184.161')
@pytest.mark.parametrize('params', [dict(language=None, country=None, timezone=None),
                                    dict(language='en', country=None, timezone=None),
                                    dict(language=None, country='IT', timezone=None),
                                    dict(language=None, country=None, timezone='UTC'),
                                    ])
def test_user_profile_ip_stack1(django_app, vcr, organization1, params):
    user = UserFactory(**params)
    url = reverse('user-profile', args=[organization1.slug])
    with vcr.use_cassette('user_profile.yaml'):
        res = django_app.get(url, user=user)
    assert res.form.submit()


@override_config(IPSTACK_KEY=os.environ.get('BITCASTER_IPSTACK_KEY'))
@mock.patch('bitcaster.web.views.user.base.get_client_ip', lambda r: '')
def test_user_profile_ip_stack_no_ip(django_app, vcr, organization1):
    user = UserFactory(language=None, country=None, timezone=None)
    url = reverse('user-profile', args=[organization1.slug])
    with vcr.use_cassette('user_profile.yaml'):
        res = django_app.get(url, user=user)
    assert res.form.submit()


@override_config(IPSTACK_KEY='123')
def test_user_profile_ip_stack_wrong_key(django_app, vcr, organization1):
    user = UserFactory(language=None, country=None, timezone=None)
    url = reverse('user-profile', args=[organization1.slug])
    with vcr.use_cassette('user_profile.yaml'):
        res = django_app.get(url, user=user)
    assert res.form.submit()


@override_config(ALLOW_CHANGE_PRIMARY_ADDRESS=True)
def test_user_profile_new_email(django_app, vcr, organization1):
    url = reverse('user-profile', args=[organization1.slug])
    res = django_app.get(url, user=organization1.owner)
    res.form['email'] = 'newemail@example.com'
    res = res.form.submit()
    assert res.status_code == 302, f"Submit failed with: {repr(res.context['form'].errors)}"
    res = res.follow()
    assert 'new email verification pending (newemail@example.com)' in str(res.body)
