# -*- coding: utf-8 -*-

from django.urls import reverse

import pytest


@pytest.mark.django_db
def test_list_languages(api_client):
    url = reverse('api:language-list')
    response = api_client.get(url, format='json')
    assert response.status_code == 200
