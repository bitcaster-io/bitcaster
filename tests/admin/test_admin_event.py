# -*- coding: utf-8 -*-
import logging

import django.core
from rest_framework.reverse import reverse

logger = logging.getLogger(__name__)


def test_event_detail(django_app, admin, event1):
    url = reverse("admin:bitcaster_event_change", args=[event1.pk])
    res = django_app.get(url, user=admin.email)
    assert res.status_code == 200


def test_event_create(django_app, admin):
    url = reverse("admin:bitcaster_event_add")
    res = django_app.get(url, user=admin.email)
    assert res.status_code == 200


def test_event_trigger(django_app, admin, subscription1, settings):
    settings.EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
    event = subscription1.event
    assert event.enabled
    assert subscription1.active
    assert subscription1.channel.enabled
    assert subscription1.channel.handler
    url = reverse("admin:bitcaster_event_trigger", [event.pk])
    res = django_app.get(url, user=admin.email)

    res = res.form.submit()
    assert res.status_code == 200
    assert django.core.mail.outbox
    mail = django.core.mail.outbox[0]
    assert mail.to == [subscription1.subscriber.email]
