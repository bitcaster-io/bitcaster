import pytest

from bitcaster.models import Counter, Occurence
from bitcaster.models.counters import get_id


@pytest.mark.django_db
def test_occurence(event1):
    obj = Occurence(event=event1)
    obj.save()
    assert str(obj)


@pytest.mark.django_db
def test_counter_initialize(event1):
    Counter.objects.initialize(event1)
    Counter.objects.increment(event1)

    assert Counter.objects.get(target=get_id(event1)).total == 1
