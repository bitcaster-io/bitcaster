import pytest
from celery.result import EagerResult

from bitcaster.models import Occurence


@pytest.mark.django_db
def test_create(event1):
    m = Occurence.log(event1)
    assert m.application is None


@pytest.mark.django_db
def test_consolidate(event1):
    m = Occurence.log(event1).consolidate(async=False)
    assert m.application == event1.application


@pytest.mark.django_db
def test_consolidate_async(event1):
    result = Occurence.log(event1).consolidate()  # async=True
    assert isinstance(result, EagerResult)
    o = result.get()
    assert o.application == event1.application
