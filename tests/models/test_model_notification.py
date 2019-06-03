import pytest

from bitcaster.models import Notification


@pytest.mark.django_db
def test_create():
    Notification.log()
