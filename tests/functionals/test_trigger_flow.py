import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from bitcaster.models import Notification, Occurence
from bitcaster.tasks.periodic import process_notifications
from bitcaster.utils.tests.factories import ApplicationTriggerKeyFactory


@pytest.mark.django_db
def test_event_trigger(subscription1):

    event1 = subscription1.event
    endpoint = reverse('api:application-event-trigger', args=[event1.application.organization.pk,
                                                         event1.application.pk,
                                                         event1.pk])

    client = APIClient()
    url = '%s?param1=**parameter-1**' % endpoint
    key = ApplicationTriggerKeyFactory(application=event1.application,
                                       events=[event1])

    client.credentials(HTTP_AUTHORIZATION='Key ' + key.token)
    ret = client.get(url, format='json')
    assert ret.status_code == 201
    o = Occurence.objects.filter(pk=ret.json()['id']).first()
    assert o.context == {'param1': '**parameter-1**'}

    n = Notification.objects.filter(occurence=o, subscription=subscription1).first()
    assert n
    assert '**parameter-1**' in n.data['message']

    #
    process_notifications()
    n.refresh_from_db()
    assert n.status == Notification.COMPLETE
