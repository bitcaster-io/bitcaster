# -*- coding: utf-8 -*-
import logging

import pytest
from django.urls import reverse

logger = logging.getLogger(__name__)

pytestmark = pytest.mark.django_db


# def test_system_channels_wizard(django_app, admin, settings):
#     settings.ON_PREMISE = False
#     res = django_app.get('/', user=admin)
#     res = res.click('Settings')
#     res = res.click('Channels')
#     res = res.click('Create channel')
#
#     res.form['a-handler'] = fqn(Email)
#     res = res.form.submit()
#     res.form['b-name'] = 'Channel1'
#     res = res.form.submit()
#
#     res.form['username'] = 'username'
#     res.form['password'] = 'password'
#     res.form['server'] = 'localhost'
#     res.form['port'] = '24'
#     res.form['sender'] = 'me@example.com'
#     res = res.form.submit().follow()
#     channel = Channel.objects.filter(name='Channel1', system=True).first()
#     assert channel
#     assert channel.config['username'] == 'username'
#     assert channel.config['password'] == 'password'
#     assert channel.config['server'] == 'localhost'


# def test_system_edit_channel(django_app, admin, system_channel, settings):
#     settings.ON_PREMISE = False
#
#     res = django_app.get(reverse('system-channel-update', args=[system_channel.pk]),
#                          user=admin)
#     res.form['name'] = 'NewName'
#     res = res.form.submit().follow()
#     assert res.status_code == 200
#     system_channel.refresh_from_db()
#     assert system_channel.name == 'NewName'


# def test_system_edit_channel_validate(django_app, admin, system_channel, settings):
#     settings.ON_PREMISE = False
#
#     res = django_app.get(reverse('system-channel-update', args=[system_channel.pk]),
#                          user=admin)
#     res.form['timeout'] = 'abc'
#     res = res.form.submit()
#     assert res.status_code == 200
#
#
# @pytest.mark.parametrize('url', ['system-channel-update', 'system-channel-toggle',
#                                  'system-channel-deprecate', 'system-channel-delete'])
# def test_system_channel_security(url, django_app, organization1, system_channel):
#     res = django_app.get(reverse(url, args=[system_channel.pk]),
#                          expect_errors=True,
#                          user=organization1.owner)
#     assert res.status_code == 403


@pytest.mark.django_db
def test_settings_general(django_app, organization1, admin):
    url = reverse('settings')
    res = django_app.get(url, user=admin)
    res.form['SITE_URL'] = 'pippo'
    res = res.form.submit()
    assert res.status_code == 200

    res.form['SITE_URL'] = 'http://localhost:80'
    res = res.form.submit()
    assert res.status_code == 302, f"Submit failed with: {repr(res.context['form'].errors)}"
    res = res.follow()
    assert res.status_code == 200


@pytest.mark.django_db
def test_settings_email(django_app, organization1, admin):
    url = reverse('settings-email')
    res = django_app.get(url, user=admin)
    res.form['EMAIL_HOST'] = 'smtp.example.org'
    res.form['EMAIL_HOST_PORT'] = '25'
    res.form['EMAIL_HOST_USER'] = 'user'
    res.form['EMAIL_HOST_PASSWORD'] = 'password'
    res = res.form.submit()
    assert res.status_code == 302, f"Submit failed with: {repr(res.context['form'].errors)}"
    res = res.follow()
    assert res.status_code == 200


@pytest.mark.django_db
def test_settings_oauth(django_app, organization1, admin):
    url = reverse('settings-oauth')
    res = django_app.get(url, user=admin)
    res = res.form.submit()
    res = res.follow()
    assert res.status_code == 200
