import pytest
from django.utils import timezone

from bitcaster.utils.reflect import fqn, package_name


class Target:
    pass


@pytest.mark.parametrize('p', [Target, Target(), fqn, 'a'])
def test_fqn(p):
    assert fqn(p)


@pytest.mark.parametrize('p', [1, timezone.now()])
def test_fqn_fail(p):
    with pytest.raises(ValueError):
        fqn(p)


def test_package_name():
    return package_name(Target) == ''
