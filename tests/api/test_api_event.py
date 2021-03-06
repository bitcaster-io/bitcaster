# -*- coding: utf-8 -*-
import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from bitcaster.utils.tests.factories import ApplicationTriggerKeyFactory


@pytest.mark.django_db
def test_api_event_list(event1, event2):
    url = reverse('api:application-event-list', args=[event1.application.organization.pk,
                                                      event1.application.pk])
    client = APIClient()

    ret = client.get(url, format='json')
    assert ret.status_code == 403

    key = event1.application.organization.owner.add_token(event1.application)
    client.credentials(HTTP_AUTHORIZATION='Token ' + key.token)
    ret = client.get(url, format='json')
    assert ret.status_code == 200
    assert len(ret.json()) == 1
    assert ret.json()[0]['id'] == event1.pk


@pytest.mark.django_db
def test_event_trigger(event1):
    url = reverse('api:application-event-trigger', args=[event1.application.organization.pk,
                                                         event1.application.pk,
                                                         event1.pk])
    client = APIClient()

    key = ApplicationTriggerKeyFactory(application=event1.application,
                                       events=[event1])

    client.credentials(HTTP_AUTHORIZATION='Key ' + key.token)
    ret = client.get(url, format='json')
    assert ret.status_code == 201


@pytest.mark.django_db
def test_event_trigger_no_auth(event1):
    url = reverse('api:application-event-trigger', args=[event1.application.organization.pk,
                                                         event1.application.pk,
                                                         event1.pk])
    client = APIClient()

    ret = client.get(url, format='json')
    assert ret.status_code == 403


@pytest.mark.django_db
def test_event_trigger_wrong_auth(event1):
    url = reverse('api:application-event-trigger', args=[event1.application.organization.pk,
                                                         event1.application.pk,
                                                         event1.pk])
    client = APIClient()

    client.credentials(HTTP_AUTHORIZATION='Key abcs')
    ret = client.get(url, format='json')
    assert ret.status_code == 403


@pytest.mark.django_db
def test_event_trigger_key_disabled(event1):
    url = reverse('api:application-event-trigger', args=[event1.application.organization.pk,
                                                         event1.application.pk,
                                                         event1.pk])
    client = APIClient()

    key = ApplicationTriggerKeyFactory(application=event1.application,
                                       enabled=False,
                                       events=[event1])

    client.credentials(HTTP_AUTHORIZATION='Key ' + key.token)
    ret = client.get(url, format='json')
    assert ret.status_code == 403


@pytest.mark.django_db
def test_event_trigger_disabled(event1):
    event1.enabled = False
    event1.save()
    url = reverse('api:application-event-trigger', args=[event1.application.organization.pk,
                                                         event1.application.pk,
                                                         event1.pk])
    client = APIClient()
    key = ApplicationTriggerKeyFactory(application=event1.application,
                                       events=[event1])
    client.credentials(HTTP_AUTHORIZATION='Key ' + key.token)
    ret = client.get(url, format='json')
    assert ret.status_code == 400
