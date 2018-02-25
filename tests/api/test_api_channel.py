import pytest
from rest_framework.reverse import reverse
from tests_utils import client_factory

from mercury.dispatchers import Email
from mercury.models import Channel
from mercury.utils import fqn


@pytest.mark.django_db
def test_channel_list(channel1):
    app = channel1.application
    url = reverse('api:application-channel-list', [app.pk])
    client = client_factory(app.owner)
    res = client.get(url)
    results = res.json()
    assert len(results) == app.channels.count() == 1


@pytest.mark.django_db
def test_channel_create(application1):
    url = reverse('api:application-channel-list', [application1.pk])
    client = client_factory(application1.owner)
    res = client.post(url, {'name': 'Name1',
                            'handler': fqn(Email),
                            'config': {'server': 'smtp.mail.com',
                                       'port': 25,
                                       'sender': 'sender@mail.com',
                                       },
                            })
    assert res.status_code == 201, str(res.content)
    result = res.json()
    channel = Channel.objects.get(pk=result['id'])
    assert channel.application == application1


# Security
@pytest.mark.django_db
def test_channel_list_wrong_owner(channel1, user2):
    """ user can only list 'owned' channels """
    app = channel1.application
    url = reverse('api:application-channel-list', args=[app.pk])
    client = client_factory(user2)
    res = client.get(url)
    assert res.status_code == 403


@pytest.mark.django_db
def test_channel_create_wrong_owner(channel1, user2):
    """ user cannot create channels for not 'owned' applications """
    app = channel1.application
    url = reverse('api:application-channel-list', [app.pk])
    client = client_factory(user2)
    res = client.post(url, {'name': 'Name1',
                            'handler': fqn(Email),
                            'config': {'server': 'smtp.mail.com',
                                       'port': 25,
                                       'sender': 'sender@mail.com',
                                       },
                            })
    assert res.status_code == 403


@pytest.mark.django_db
def test_channel_create_invalid_handler(application1):
    """ channel creations needvalid against handler"""
    url = reverse('api:application-channel-list', [application1.pk])
    client = client_factory(application1.owner)
    res = client.post(url, {'name': 'Name1',
                            'handler': '---',
                            'config': {'server': 'smtp.mail.com',
                                       'port': 25,
                                       'sender': 'sender@mail.com',
                                       },
                            })
    assert res.status_code == 400, str(res.content)


@pytest.mark.django_db
def test_channel_create_invalid_handler_configuration(application1):
    """ channel creations need to be validated against handler validator"""
    url = reverse('api:application-channel-list', [application1.pk])
    client = client_factory(application1.owner)
    res = client.post(url, {'name': 'Name1',
                            'handler': '---',
                            'config': {'server': 'smtp.mail.com',
                                       'port': '--',
                                       'sender': 'sender@mail.com',
                                       },
                            })
    assert res.status_code == 400, str(res.content)


@pytest.mark.django_db
def test_channel_update_invalid(channel1):
    application1 = channel1.application
    url = reverse('api:application-channel-detail', [application1.pk, channel1.pk])
    client = client_factory(application1.owner)
    res = client.patch(url, {'name': 'Name21',
                             'config': {'server': '--',
                                        'sender': 'sender@mail.com',
                                        },
                             })
    assert res.status_code == 400, str(res.content)


@pytest.mark.django_db
def test_channel_enable_check_config(channel1):
    application1 = channel1.application
    channel1.enabled = False
    channel1.config = {}
    channel1.save()
    url = reverse('api:application-channel-detail', [application1.pk, channel1.pk])
    client = client_factory(application1.owner)
    res = client.patch(url, {'enabled': True})
    payload = res.json()
    assert res.status_code == 400, str(res.content)
    assert payload['config'] == [{'port': ['A valid integer is required.'],
                                  'sender': ['This field may not be blank.'],
                                  'server': ['This field may not be blank.']}]
