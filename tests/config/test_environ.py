import pytest
from django.core.exceptions import ImproperlyConfigured

from bitcaster.config.environ import Env

PARAMS = [(int, Env.NOTSET),
          (str, '2'),
          str,
          (str,),
          (str, '$TEST_CC'),
          ]


@pytest.mark.parametrize('value', PARAMS)
def test_environ(value):
    env = Env('TEST_', AA=value)
    env.ENVIRON = {'TEST_AA': '1'}
    assert env.AA


@pytest.mark.parametrize('value', [int, (int,)])
def test_environ_invalid(value):
    env = Env('TEST_', AA=value)
    with pytest.raises(ImproperlyConfigured):
        assert env.AA


def test_environ_proxy():
    env = Env('TEST_', AA=(str, 'aa'))
    env.ENVIRON = {'TEST_BB': 'bb', 'TEST_AA': '${TEST_BB}'}
    assert env.AA == 'bb'


def test_environ_cast():
    env = Env('TEST_', AA=(bool,))
    env.ENVIRON = {'TEST_AA': 'true'}
    assert env.bool('AA')
    assert env('AA')
