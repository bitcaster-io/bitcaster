# -*- coding: utf-8 -*-
from unittest.mock import Mock

import pytest

from bitcaster.dispatchers import Email


@pytest.mark.django_db
def test_email(subscription1):
    channel = Mock(config={'server': 'dummy',
                           'port': 25,
                           'backend': 'django.core.mail.backends.locmem.EmailBackend',
                           'sender': 'from@dummy.org'})
    d = Email(channel)
    assert d.emit(subscription1, 'subject', 'message') == 1


@pytest.mark.django_db
def test_email_test_connection(subscription1):
    channel = Mock(config={'server': 'dummy',
                           'port': 25,
                           'backend': 'django.core.mail.backends.locmem.EmailBackend',
                           'sender': 'from@dummy.org'})
    d = Email(channel)
    assert d.test_connection()
