import pytest
from django.core.exceptions import ValidationError

from bitcaster.framework.db.validators import (RateLimitValidator,
                                               ReservedWordValidator,)


def test_ReservedWordValidator():
    v = ReservedWordValidator()
    v('valid')
    with pytest.raises(ValidationError):
        v('superuser')


def test_RateLimitValidator():
    v = RateLimitValidator()
    v('1/s')
