
import pytest

from bitcaster.models import Event


@pytest.mark.django_db
def test_create(application1):
    c = Event(application=application1)
    c.clean()
    c.save()
    assert c.pk


@pytest.mark.django_db
def test_valid_channels(event1):
    assert not event1.valid_channels


@pytest.mark.django_db
def test_enabled_channels(event1):
    assert event1.enabled_channels
