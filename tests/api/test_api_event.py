# -*- coding: utf-8 -*-
import pytest
from django.urls import reverse
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_event_trigger(event1):
    url = reverse('api:application-event-trigger', args=[event1.application.pk,
                                                         event1.pk])
    client = APIClient()

    key = event1.application.organization.owner.add_trigger(event1.application)
    client.credentials(HTTP_AUTHORIZATION='Token ' + key.token)
    ret = client.get(url, format='json')
    assert ret.status_code == 201


@pytest.mark.django_db
def test_event_trigger_no_auth(event1):
    url = reverse('api:application-event-trigger', args=[event1.application.pk,
                                                         event1.pk])
    client = APIClient()

    ret = client.get(url, format='json')
    assert ret.status_code == 403


@pytest.mark.django_db
def test_event_trigger_disabled(event1):
    event1.enabled = False
    event1.save()
    url = reverse('api:application-event-trigger', args=[event1.application.pk,
                                                         event1.pk])
    client = APIClient()
    key = event1.application.organization.owner.add_trigger(event1.application)
    client.credentials(HTTP_AUTHORIZATION='Token ' + key.token)
    ret = client.get(url, format='json')
    assert ret.status_code == 400
