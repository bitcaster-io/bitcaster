import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from bitcaster.models import DispatcherMetaData, Notification, Occurence
from bitcaster.tasks.periodic import process_notifications
from bitcaster.utils.reflect import fqn
from bitcaster.utils.tests.factories import ApplicationTriggerKeyFactory


@pytest.mark.django_db
@pytest.mark.parametrize('filter', ['address', 'email', 'custom:index_number'])
def test_event_batch_flow(subscription1, subscription2, monkeypatch, filter):
    monkeypatch.setattr('%s.objects.is_enabled' % fqn(DispatcherMetaData),
                        lambda handler: True)

    monkeypatch.setattr('bitcaster.system.stopped', lambda: False)

    # user1.assignments.create(address=addr, channel=message1.channel)

    user = subscription1.subscriber
    address1 = subscription1.get_address()
    # DispatcherMetaData.objects.inspect()
    # DispatcherMetaData.objects.enable_valid()

    event1 = subscription1.event
    url = reverse('api:application-event-batch', args=[event1.application.organization.pk,
                                                       event1.application.pk,
                                                       event1.pk])

    client = APIClient()
    key = ApplicationTriggerKeyFactory(application=event1.application,
                                       events=[event1])

    client.credentials(HTTP_AUTHORIZATION='Key ' + key.token)
    payload = {'filter': filter,
               'arguments': {'param1': '**parameter-1**'},
               'targets': [address1]
               }
    if filter == 'email':
        payload['targets'] = [user.email]

    elif filter == 'custom:index_number':
        payload['targets'] = ['__%s__' % user.email]

    ret = client.post(url, payload, format='json')

    assert ret.status_code == 201
    o = Occurence.objects.filter(pk=ret.json()['id']).first()
    # assert o.context == {'param1': '**parameter-1**'}

    n = Notification.objects.get(occurence=o, subscription=subscription1)
    assert not Notification.objects.filter(occurence=o, subscription=subscription2).exists()

    process_notifications()
    n.refresh_from_db()
    assert n.status == Notification.COMPLETE
