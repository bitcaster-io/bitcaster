import pytest

from bitcaster.logging import log_notification, log_occurence

pytestmark = pytest.mark.django_db


def test_log_notification(subscription1):
    entry = log_notification(subscription1)
    assert entry.pk


def test_log_occurence(event1):
    entry = log_occurence(event1)
    assert entry.pk
