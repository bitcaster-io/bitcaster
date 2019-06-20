# -*- coding: utf-8 -*-
import logging

import pytest
from rest_framework.reverse import reverse

logger = logging.getLogger(__name__)

pytestmark = pytest.mark.django_db


def test_event_detail(django_app, admin, event1):
    url = reverse('admin:bitcaster_event_change', args=[event1.pk])
    res = django_app.get(url, user=admin.email)
    assert res.status_code == 200


def test_event_create(django_app, admin):
    url = reverse('admin:bitcaster_event_add')
    res = django_app.get(url, user=admin.email)
    assert res.status_code == 200
