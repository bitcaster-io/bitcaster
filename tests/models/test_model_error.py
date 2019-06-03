import pytest

from bitcaster.models import ErrorEntry


@pytest.mark.django_db
def test_log(event1):
    c = ErrorEntry.log(target=event1)
    c.clean()
    c.save()
    assert c.pk
