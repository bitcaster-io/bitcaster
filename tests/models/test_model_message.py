import pytest
from django.core.exceptions import ValidationError
from strategy_field.utils import fqn

from bitcaster.dispatchers import Twitter
from bitcaster.models import Channel, Message


def test_str():
    obj = Message(name='test')
    assert str(obj)


@pytest.mark.django_db
def test_create(event1, channel1):
    obj = Message(name='test', event=event1, channel=channel1)
    obj.save()
    assert obj.pk


def test_parse_body():
    obj = Message(name='test', body='{param}')
    assert obj.parse_body({'param': 'abc'}) == 'abc'


@pytest.mark.django_db
def test_clean_validate_message(application1):
    obj = Message(name='test',
                  body='1' * 200,  # Twitter only allows 140 chars
                  enabled=True,
                  channel=Channel(application=application1,
                                  organization=application1.organization,
                                  handler=fqn(Twitter))
                  )

    with pytest.raises(ValidationError):
        obj.clean()


@pytest.mark.django_db
def test_clean_skip_message_validation(application1):
    obj = Message(name='test',
                  body='1' * 200,  # Twitter only allows 140 chars
                  enabled=False,
                  channel=Channel(application=application1,
                                  organization=application1.organization,
                                  handler=fqn(Twitter))
                  )
    obj.clean()
    assert True
