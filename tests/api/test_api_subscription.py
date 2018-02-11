import logging

from rest_framework.reverse import reverse

from mercury.utils.tests.factories import client_factory

logger = logging.getLogger(__name__)


def test_subscription_list(subscription1, subscription2):
    user1 = subscription1.subscriber
    client = client_factory(user1)
    url = reverse('api:user-subscription-list', args=[user1.pk])
    res = client.get(url)
    assert res.status_code == 200, str(res.content)
    result = res.json()
    assert len(result) == user1.subscriptions.count()


def test_subscription_create(user1, message2):
    url = reverse('api:user-subscription-list', args=[user1.pk])
    client = client_factory(user1)
    res = client.post(url, {'channel': message2.channels.first().pk,
                            'config': "{}",
                            'event': message2.event.pk})
    assert res.status_code == 201, str(res.content)
    result = res.json()
    subscription = user1.subscriptions.latest()
    assert subscription.pk == result['id']


def test_subscription_udate(subscription1, channel2):
    url = reverse('api:user-subscription-detail', args=[subscription1.subscriber.pk,
                                                        subscription1.pk])
    client = client_factory(subscription1.subscriber)
    res = client.patch(url, {'channel': channel2.pk})
    assert res.status_code == 200, str(res.content)
    subscription1.refresh_from_db()
    assert subscription1.channel == channel2


def test_subscription_filter(subscription1, subscription2, admin):
    user1 = subscription1.subscriber
    client = client_factory(user1)
    url = reverse('api:user-subscription-list', args=[user1.pk])
    res = client.get(url)
    assert res.status_code == 200, str(res.content)
    result = res.json()
    assert len(result) == user1.subscriptions.count()

    # client = client_factory(user1)
    # url = reverse('api:subscription-list')
    # res = client.get(url)
    # assert res.status_code == 200, str(res.content)
    # result = res.json()
    # assert len(result) == 0

    # client = client_factory(admin)
    # url = reverse('api:subscription-list')
    # res = client.get(url)
    # assert res.status_code == 200, str(res.content)
    # result = res.json()
    # assert len(result) == 2


def test_subscription_create_invalid(user1, channel2, event2):
    """user is not allowed to subscribe to events if no messages are configured"""
    url = reverse('api:user-subscription-list', args=[user1.pk])
    client = client_factory(user1)
    res = client.post(url, {'channel': channel2.pk,
                            'event': event2.pk})
    assert res.status_code == 400, str(res.content)
