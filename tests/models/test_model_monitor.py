import pytest

from bitcaster.models import Monitor


@pytest.mark.django_db
def test_create(application1):
    m = Monitor(application=application1)
    m.save()
    assert m.pk
