# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import pytest
from rest_framework.reverse import reverse
from tests_utils import APIClient, client_factory

from mercury import models
from mercury.models import Event


@pytest.mark.django_db
def test_event_list(event1):
    app = event1.application
    url = reverse('api:application-event-list', args=[app.pk])
    client = client_factory(app.owner)
    res = client.get(url)
    assert res.status_code == 200


@pytest.mark.django_db
def test_event_create(application1):
    url = reverse('api:application-event-list', args=[application1.pk])
    client = client_factory(application1.organization.owner)
    res = client.post(url, {'name': 'Event1'})
    assert res.status_code == 201, str(res.content)
    result = res.json()
    event = Event.objects.get(pk=result['id'])
    assert event.application == application1


@pytest.mark.django_db
def test_event_update(event1):
    application = event1.application
    url = reverse('api:application-event-detail', args=[application.pk, event1.pk])
    client = client_factory(application.organization.owner)
    res = client.put(url, {'name': 'Event21'})
    assert res.status_code == 200, str(res.content)


@pytest.mark.django_db
def test_event_delete(event1):
    application = event1.application
    url = reverse('api:application-event-detail', args=[application.pk, event1.pk])
    client = client_factory(application.organization.owner)
    res = client.delete(url)
    assert res.status_code == 204, str(res.content)
    with pytest.raises(Event.DoesNotExist):
        event1.refresh_from_db()


@pytest.mark.django_db
def test_event_trigger(event1):
    # do not use api_client_factory for test readability
    app = event1.application
    # token = models.ApiAuthToken.objects.get(application=app)
    token = models.ApiTriggerKey.objects.get(application=app)
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION='Token ' + token.token)
    url = reverse('api:application-event-trigger', args=[app.pk, event1.pk])
    res = client.get(url, {'message': 'ABC'})
    assert res.status_code == 201, str(res.content)


@pytest.mark.django_db
def test_event_trigger_require_token(event1):
    """ event can only be used using token never credentials"""
    app = event1.application
    # do not use api_client_factory for test readability
    client = APIClient()
    client.login(username=app.owner.username, password='123')
    url = reverse('api:application-event-trigger', args=[app.pk, event1.pk])
    res = client.get(url, {'message': 'ABC'})
    assert res.status_code == 403, str(res.content)


@pytest.mark.django_db
def test_event_trigger_check_token(event1, token1):
    app = event1.application
    # do not use api_client_factory for test readability
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION='TriggerToken ' + token1.token)
    url = reverse('api:application-event-trigger', args=[app.pk, event1.pk])
    res = client.get(url, {'message': 'ABC'})
    assert res.status_code == 403, str(res.content)
