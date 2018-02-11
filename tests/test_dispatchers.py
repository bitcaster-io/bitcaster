# -*- coding: utf-8 -*-
from unittest.mock import Mock

from mercury.dispatchers import Email, Gmail


def test_email(subscription1):
    channel = Mock(config={'server': 'dummy',
                           'port': 25,
                           'sender': 'from@dummy.org'})
    d = Email(channel)
    assert d.emit(subscription1, 'subject', 'message') == 1


def test_email_test_connection(subscription1):
    channel = Mock(config={'server': 'dummy',
                           'port': 25,
                           'sender': 'from@dummy.org'})
    d = Email(channel)
    assert d.test_connection()


def test_gmail(subscription1):
    channel = Mock(config={'sender': 'from@dummy.org',
                           'username': 'user',
                           'password': 'password'})
    d = Gmail(channel)
    assert d.emit(subscription1, 'subject', 'message') == 1


def test_gmail_test_connection(subscription1):
    channel = Mock(config={'sender': 'from@dummy.org',
                           'username': 'user',
                           'password': 'password'})
    d = Gmail(channel)
    assert d.test_connection()
