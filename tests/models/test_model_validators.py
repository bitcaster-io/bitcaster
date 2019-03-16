import pytest
from django.core.exceptions import ValidationError

from bitcaster.models.validators import ListValidator

pytestmark = pytest.mark.django_db


def test_listvalidator():
    v = ListValidator(['a', 'b'])
    with pytest.raises(ValidationError):
        v('a')
    assert v('x') is None
