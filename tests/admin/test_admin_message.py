# -*- coding: utf-8 -*-
import logging

from rest_framework.reverse import reverse

logger = logging.getLogger(__name__)


def test_message_detail(django_app, admin, message1):
    url = reverse("admin:bitcaster_message_change", args=[message1.pk])
    res = django_app.get(url, user=admin.email)
    assert res.status_code == 200


def test_message_create(django_app, admin):
    url = reverse("admin:bitcaster_message_add")
    res = django_app.get(url, user=admin.email)
    assert res.status_code == 200
