from unittest import mock
from unittest.mock import Mock

from bitcaster.utils.django import (activator_factory,
                                    deactivator_factory, toggler_factory,)


def test_toggler_factory():
    with mock.patch('bitcaster.utils.django.get_connection'):
        func = toggler_factory('test')
        assert func(Mock(), Mock(), Mock())


def test_activator_factory():
    with mock.patch('bitcaster.utils.django.get_connection'):
        func = activator_factory('test')
        assert func(Mock(), Mock(), Mock())


def test_deactivator_factory():
    with mock.patch('bitcaster.utils.django.get_connection'):
        func = deactivator_factory('test')
        assert func(Mock(), Mock(), Mock())
