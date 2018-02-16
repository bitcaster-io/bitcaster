# -*- coding: utf-8 -*-
from unittest.mock import Mock

from mercury.dispatchers import Email


def test_email(subscription1):
    channel = Mock(config={'server': 'dummy',
                           'port': 25,
                           'backend': 'django.core.mail.backends.locmem.EmailBackend',
                           'sender': 'from@dummy.org'})
    d = Email(channel)
    assert d.emit(subscription1, 'subject', 'message') == 1


def test_email_test_connection(subscription1):
    channel = Mock(config={'server': 'dummy',
                           'port': 25,
                           'backend': 'django.core.mail.backends.locmem.EmailBackend',
                           'sender': 'from@dummy.org'})
    d = Email(channel)
    assert d.test_connection()
