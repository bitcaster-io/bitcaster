import pytest

pytestmark = pytest.mark.django_db


def test_tsdb(notification1):
    from bitcaster.tsdb.logging import broker
    ts = broker.get_ts(notification1.application.organization.pk)
    ts.log_notification(notification1)

    # ts.record_hit(EVENT)
    # TODO: remove me
    # print(111, "test_tsdb.py:23", ts.get_hits(EVENT, MINUTE, 3))
