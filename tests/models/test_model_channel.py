from unittest import mock
from unittest.mock import Mock

import pytest
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from strategy_field.utils import fqn

from bitcaster.dispatchers import Gmail, Twitter
from bitcaster.exceptions import MaxChannelError, PluginValidationError
from bitcaster.models import Channel, Message
from bitcaster.utils.tests.factories import ChannelFactory


@pytest.mark.django_db
def test_create(organization1):
    c = Channel(organization=organization1,
                handler=Gmail)
    c.clean()
    c.save()
    assert c.pk

    c = Channel()
    c.clean()
    c.save()
    assert c.pk


@pytest.mark.django_db
def test_str(channel1):
    assert str(channel1)


@pytest.mark.django_db
def test_clean(channel1):
    c = Channel()
    c.clean()

    c = Channel(enabled=True)
    with pytest.raises(ValidationError) as e:
        c.clean()
    assert e.value.message == 'Cannot enable Channel without handler'

    c = Channel(enabled=True, handler=fqn(Gmail))
    with pytest.raises(ValidationError) as e:
        c.clean()
    assert e.value.message == 'Configure channel before enable it'

    c = Channel(enabled=True, handler=fqn(Gmail), config=Gmail.get_full_config({}))
    with pytest.raises(ValidationError) as e:
        c.clean()
    assert e.value.message == 'Configure channel before enable it'

    channel1.clean()
    assert channel1.is_configured


@pytest.mark.django_db
def test_validate_address(channel1):
    with pytest.raises(PluginValidationError):
        assert not channel1.validate_address('---')
    assert channel1.validate_address('test@example.com')


@pytest.mark.django_db
def test_validate_message(application1):
    ch = ChannelFactory(application=application1,
                        organization=application1.organization,
                        handler=fqn(Twitter)
                        )

    with pytest.raises(ValidationError):
        ch.validate_message(Message(body='1' * 200))


@pytest.mark.django_db
def test_validate_subscription(subscription1):
    channel = subscription1.channel
    with pytest.raises(PluginValidationError):
        assert channel.validate_subscription(Mock())
    assert channel.validate_subscription(subscription1)


@pytest.mark.django_db
def test_is_configured(channel1):
    assert channel1.is_configured
    assert not Channel().is_configured


@pytest.mark.django_db
def test_get_usage_message(channel1):
    assert channel1.get_usage_message() is not None


@pytest.mark.django_db
def test_get_usage(channel1):
    assert channel1.get_usage() is not None


@pytest.mark.django_db
def test_process_event(subscription1):
    channel = subscription1.channel
    event = subscription1.event
    assert channel.process_event(event, {})


@pytest.mark.django_db
def test_process_event_errors_threshold(subscription1):
    channel = subscription1.channel
    channel.errors_threshold = 0
    event = subscription1.event
    with pytest.raises(MaxChannelError):
        with mock.patch('bitcaster.models.Channel.handler', side_effect=Mock(side_effect=Exception)):
            assert channel.process_event(event, {})
    assert not channel.enabled


@pytest.mark.django_db
def test_process_event_no_messages(subscription1):
    channel = subscription1.channel
    channel.messages.all().delete()
    event = subscription1.event
    with pytest.raises(ObjectDoesNotExist):
        assert channel.process_event(event, {})


@pytest.mark.django_db
def test_process_disabled_event(subscription1):
    channel = Channel(enabled=False)
    assert channel.process_event(Mock(), {}) == (0, 0)


@pytest.mark.django_db
def test_valid(channel1):
    assert Channel.objects.valid()


@pytest.mark.django_db
def test_selectable(channel1, application1):
    assert Channel.objects.selectable(application1)
