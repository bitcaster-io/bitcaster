# -*- coding: utf-8 -*-
import pytest
from django.urls import reverse
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_api_application_filter(event1, event2):
    url = reverse('api:application-list')
    client = APIClient()

    ret = client.get(url, format='json')
    assert ret.status_code == 403

    key = event1.application.organization.owner.add_token(event1.application)
    client.credentials(HTTP_AUTHORIZATION='Token ' + key.token)
    ret = client.get(url, format='json')
    assert ret.status_code == 200
    assert len(ret.json()) == 1
    assert ret.json()[0]['id'] == event1.application.pk
