import time

import pytest

from bitcaster.tsdb.db import counters, stats

pytestmark = pytest.mark.django_db


def test_tsdb_log_notification(organization1):
    stats.log_notification(organization1)


def test_errors():
    key = 'test-%s' % time.time()
    counters.increase(key)
    counters.increase(key)
    assert counters.get_buckets(key, 'd', 1)[0][1] == 2
