# -*- coding: utf-8 -*-
import json
import logging

import django_webtest
import pytest
from rest_framework.reverse import reverse
from strategy_field.utils import fqn

from bitcaster.dispatchers import Email
from bitcaster.models import Channel

logger = logging.getLogger(__name__)

pytestmark = pytest.mark.django_db

def test_channel_create(django_app, admin, application1):
    url = reverse("admin:bitcaster_channel_add")
    name = "Test-Application-1"
    res = django_app.get(url, user=admin.email)
    res.form['name'] = name
    res.form['application'] = application1.pk
    res.form['handler'] = fqn(Email)
    res = res.form.submit().follow()
    res = res.click(name, index=1)  # 1 so we test also that 2 links have to exists
    channel = res.context['original']
    assert isinstance(channel.handler, Email)


def test_channel_configure(django_app, admin, channel1):
    url = reverse("admin:bitcaster_channel_configure", args=[channel1.pk])
    res = django_app.get(url, user=admin.email)
    res.form['port'] = 587
    res = res.form.submit()
    assert res.status_code == 302


def test_channel_fail_configure(django_app, admin, channel1):
    url = reverse("admin:bitcaster_channel_configure", args=[channel1.pk])
    res = django_app.get(url, user=admin.email)
    res.form['port'] = json.dumps({'port': 'abc'})
    res = res.form.submit()
    assert res.status_code == 200
    assert 'port' in res.context['serializer'].errors


def test_channel_fail(django_app, admin, channel1):
    url = reverse("admin:bitcaster_channel_change", args=[channel1.pk])
    res = django_app.get(url, user=admin.email)
    res.form['handler'].force_value('0000')
    res = res.form.submit()
    assert 'handler' in res.context['adminform'].form.errors
    assert res.status_code == 200


@pytest.mark.parametrize("action", ["validate_channel", "activate", "deactivate"])
def test_channel_adminaction_bulk(action, django_app: django_webtest.DjangoTestApp,
                                  admin, channel1: Channel):
    url = reverse("admin:bitcaster_channel_changelist")
    res = django_app.get(url, user=admin.email)
    res.form['action'] = action
    res.form['_selected_action'] = [channel1.pk]
    res = res.form.submit()
    assert res.status_code == 302
    assert channel1.enabled


@pytest.mark.parametrize("extra_action", ["Test"])
def test_channel_action_bulk(extra_action, django_app: django_webtest.DjangoTestApp,
                             admin, channel1: Channel):
    url = reverse("admin:bitcaster_channel_change", args=[channel1.pk])
    res = django_app.get(url, user=admin.email)
    res = res.click(extra_action)
    assert res.status_code == 302


@pytest.mark.extra_urls_action
def test_channel_test(django_app, admin, channel1):
    url = reverse("admin:bitcaster_channel_test", args=[channel1.pk])
    res = django_app.get(url, user=admin.email)
    assert res.status_code == 302, res.showbrowser()


@pytest.mark.extra_urls_action
def test_channel_send_sample_message(django_app, admin, channel1):
    url = reverse("admin:bitcaster_channel_send_sample_message", args=[channel1.pk])
    res = django_app.get(url, user=admin.email)
    res.form["email"] = "sample@mailnator.com"
    res = res.form.submit()
    assert res.status_code == 302


def test_channel_test1(django_app, admin, channel1, monkeypatch):
    monkeypatch.setattr('bitcaster.dispatchers.email.Email.test_connection',
                        lambda *args: True)
    url = reverse("admin:bitcaster_channel_test", args=[channel1.pk])

    res = django_app.get(url, user=admin.email)
    assert res.status_code == 302


def test_channel_list(django_app, admin, channel1):
    url = reverse("admin:bitcaster_channel_changelist")
    res = django_app.get(url, user=admin.email)
    assert res.status_code == 200
