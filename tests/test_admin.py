# -*- coding: utf-8 -*-
import django.core.mail
import json

from rest_framework.reverse import reverse


# application
def test_application_detail(django_app, admin, application1):
    url = reverse("admin:mercury_application_change", args=[application1.pk])
    res = django_app.get(url, user=admin.username)
    assert res.status_code == 200


# channel
def test_channel_fail(django_app, admin, channel1):
    url = reverse("admin:mercury_channel_change", args=[channel1.pk])
    res = django_app.get(url, user=admin.username)
    res.form['config'] = json.dumps({'port': 'abc'})
    res = res.form.submit()
    assert res.status_code == 200
    assert 'config' in res.context['adminform'].form.errors

    res.form['config'] = {}
    res.form['handler'].force_value('0000')
    res = res.form.submit()
    assert 'handler' in res.context['adminform'].form.errors
    assert res.status_code == 200


def test_channel_test(django_app, admin, channel1):
    url = reverse("admin:mercury_channel_test", args=[channel1.pk])
    res = django_app.get(url, user=admin.username)
    assert res.status_code == 302


def test_channel_test1(django_app, admin, channel1, monkeypatch):
    monkeypatch.setattr('mercury.dispatchers.email.Email.test_connection',
                        lambda *args: True)
    url = reverse("admin:mercury_channel_test", args=[channel1.pk])

    res = django_app.get(url, user=admin.username)
    assert res.status_code == 302


def test_channel_list(django_app, admin, channel1):
    url = reverse("admin:mercury_channel_changelist")
    res = django_app.get(url, user=admin.username)
    assert res.status_code == 200


# message
def test_message_detail(django_app, admin, message1):
    url = reverse("admin:mercury_message_change", args=[message1.pk])
    res = django_app.get(url, user=admin.username)
    assert res.status_code == 200


def test_message_create(django_app, admin):
    url = reverse("admin:mercury_message_add")
    res = django_app.get(url, user=admin.username)
    assert res.status_code == 200


# event
def test_event_detail(django_app, admin, event1):
    url = reverse("admin:mercury_event_change", args=[event1.pk])
    res = django_app.get(url, user=admin.username)
    assert res.status_code == 200


def test_event_create(django_app, admin):
    url = reverse("admin:mercury_event_add")
    res = django_app.get(url, user=admin.username)
    assert res.status_code == 200


def test_event_trigger(django_app, admin, subscription1, settings):
    settings.EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
    event = subscription1.event
    assert event.enabled
    assert subscription1.active
    assert subscription1.channel.enabled
    assert subscription1.channel.handler
    url = reverse("admin:mercury_event_trigger", [event.pk])
    res = django_app.get(url, user=admin.username)

    res = res.form.submit()
    assert res.status_code == 200
    assert django.core.mail.outbox
    mail = django.core.mail.outbox[0]
    assert mail.to == [subscription1.subscriber.email]
