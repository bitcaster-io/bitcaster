import pytest

from bitcaster.models import ApplicationTriggerKey


@pytest.mark.django_db
def test_create(application1):
    m = ApplicationTriggerKey(name='key1')
    assert str(m)
