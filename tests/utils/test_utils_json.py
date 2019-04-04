import datetime
from decimal import Decimal
from uuid import uuid4

import pytest
import pytz
from django.utils import timezone
from django.utils.functional import SimpleLazyObject, lazy
from django.utils.translation import ugettext_lazy

from bitcaster.utils.json import Decoder, Encoder

PARAMS = [[2, 3], uuid4(),
          timezone.now(),
          datetime.datetime.today(),  # note: without timezone
          'a',
          pytz.timezone('UTC'),
          lazy,
          SimpleLazyObject(lambda: 'aa'),
          ugettext_lazy('aaa'),
          {'a': 1}]
IDS = [type(i).__name__ for i in PARAMS]


@pytest.mark.parametrize('param', PARAMS, ids=IDS)
def test_encoder(param):
    encoded = Encoder().encode(param)
    decoded = Decoder().decode(encoded)
    assert param == decoded


@pytest.mark.parametrize('param', [Decimal('1.1')])
def test_encoder_not_supported(param):
    with pytest.raises(TypeError):
        Encoder().encode(param)
