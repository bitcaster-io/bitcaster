# import os
#
# import pytest
#
# from bitcaster.dispatchers import Facebook
# from bitcaster.utils.tests.dispatcher_testcase import DispatcherBaseTest
#
# pytestmark = pytest.mark.django_db
#
#
# @pytest.mark.skipif_missing('TEST_FACEBOOK_ACCOUNT', 'TEST_FACEBOOK_KEY', 'TEST_FACEBOOK_PASSWORD')
# @pytest.mark.django_db
# class TestDispatcherFacebook(DispatcherBaseTest):
#     TARGET = Facebook
#     CONFIG = {'account': os.environ.get('TEST_FACEBOOK_ACCOUNT'),
#               'key': os.environ.get('TEST_FACEBOOK_KEY'),
#               'password': os.environ.get('TEST_FACEBOOK_PASSWORD')}
#     RECIPIENT = os.environ.get('TEST_FACEBOOK_RECIPIENT')
