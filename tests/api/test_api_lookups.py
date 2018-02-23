# -*- coding: utf-8 -*-

import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_list_languages(api_client):
    url = reverse('api:language-list')
    response = api_client.get(url, format='json')
    assert response.status_code == 200
