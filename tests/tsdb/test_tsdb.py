# import pytest
# from django.conf import settings
# from redis import StrictRedis
#
# from bitcaster.tsdb.db import TARGETS, TS
#
# pytestmark = pytest.mark.django_db
#
#
# @pytest.fixture()
# def tsdb():
#     return TS(StrictRedis.from_url(settings.TSDB_STORE),
#               'test')
#
#
# @pytest.mark.parametrize('target', TARGETS)
# def test_tsdb_notification(tsdb, target):
#     tsdb.notification.log(1, target)
#
#
# @pytest.mark.parametrize('target', TARGETS)
# def test_tsdb_error(tsdb, target):
#     tsdb.error.log(1, target)
#
#
# @pytest.mark.parametrize('target', ['event'])
# def test_tsdb_occurence(tsdb, target):
#     tsdb.occurence.log(1, target)
#
#
# @pytest.mark.parametrize('target', ['organization', 'event'])
# def test_tsdb_confirmation(tsdb, target):
#     tsdb.confirmation.log(1, target)
#
#
# @pytest.mark.parametrize('target', ['organization', 'channel'])
# def test_tsdb_buffer(tsdb, target):
#     tsdb.buffer.log(1, target)
