import pytest
from django.core.exceptions import ValidationError

from bitcaster.models import Monitor

pytestmark = pytest.mark.django_db


def test_create(application1):
    m = Monitor(application=application1)
    m.save()
    assert m.pk


def test_str(application1):
    m = Monitor(application=application1, name='monitor1')
    assert str(m)


def test_handler_name(monitor1):
    assert monitor1.handler_name


@pytest.mark.skipif_missing('TEST_MONITOR_USER', 'TEST_MONITOR_PASSWORD', 'TEST_MONITOR_FOLDER')
def test_validate_configuration(monitor1):
    monitor1.handler.validate_configuration(monitor1.config)


@pytest.mark.skipif_missing('TEST_MONITOR_USER', 'TEST_MONITOR_PASSWORD', 'TEST_MONITOR_FOLDER')
def test_is_configured(monitor1):
    assert monitor1.is_configured


def test_not_is_configured():
    assert not Monitor().is_configured


def test_clean_fail():
    m = Monitor(enabled=True)
    with pytest.raises(ValidationError):
        m.clean()


def test_clean(monitor1):
    monitor1.clean()


# MonitorQuerySet

def test_valid(monitor1):
    assert Monitor.objects.valid()
