import pytest

from bitcaster.models import Notification


@pytest.mark.django_db
def test_log(address1, subscription1):
    assert Notification.log(address1, subscription1, {})
