# -*- coding: utf-8 -*-
import time

import pytest

from bitcaster.utils.locks import get
from bitcaster.utils.retries import RetryException, TimedRetryPolicy


def test_get_lock():
    key = str(time.time())
    assert get(key, 2, 2).acquire()
    assert get(key, 2, 2).acquire()


def test_get_lock_fail():
    key = str(time.time())
    assert get(key, 60, 60).acquire()
    assert not get(key, 2, 2).acquire()


def test_time_retry():
    key = str(time.time())
    assert get(key, 60, 1).acquire()
    lock = get(key, 60, 1)
    with pytest.raises(RetryException):
        with TimedRetryPolicy(5, lock.acquire):
            pass
