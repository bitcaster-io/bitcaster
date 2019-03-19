import pytest

from bitcaster.models import Organization

pytestmark = pytest.mark.django_db


def test_deletable(organization1):
    assert Organization.objects.valid()
