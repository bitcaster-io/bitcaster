# # -*- coding: utf-8 -*-
# import time
#
# import pytest
#
# from bitcaster.utils.locks import get
# from bitcaster.utils.retries import RetryException, TimedRetryPolicy
#
#
# def test_get_lock():
#     key = str(time.time())
#     assert get(key, 2, 2).acquire()
#     assert get(key, 2, 2).acquire()
#
#
# def test_get_lock_fail():
#     key = str(time.time())
#     assert get(key, 60, 60).acquire()
#     assert not get(key, 2, 2).acquire()
#
#
# def test_time_retry_fail():
#     key = str(time.time())
#     assert get(key, 1, 60).acquire()
#     lock = get(key, 1, 60)
#     with pytest.raises(RetryException):
#         with TimedRetryPolicy(5, lock.acquire):
#             pass
#
#
# def test_time_retry():
#     key = str(time.time())
#     lock = get(key, 1, 60)
#     with TimedRetryPolicy(5, lock.acquire):
#         assert True
#
#
# def test_time_retry_custom_delay():
#     key = str(time.time())
#     assert get(key, 2, 2).acquire()
#     lock = get(key, 2, 2)
#     with TimedRetryPolicy(10, lock.acquire, delay=lambda i: 1):
#         assert True
