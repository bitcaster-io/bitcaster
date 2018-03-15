# -*- coding: utf-8 -*-
import pytest
from rest_framework.reverse import reverse

# application


@pytest.mark.django_db
def test_application_detail(django_app, admin, application1):
    url = reverse("admin:bitcaster_application_change", args=[application1.pk])
    res = django_app.get(url, user=admin.email)
    assert res.status_code == 200
