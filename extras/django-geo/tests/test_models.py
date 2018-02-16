import pytest

from geo.models import Country


@pytest.mark.django_db
def test_country_manager(italy, usa):
    assert Country.objects.north_america().count() == 1
    assert Country.objects.europe().count() == 1

    assert Country.objects.oceania().count() == 0
    assert Country.objects.antartica().count() == 0
    assert Country.objects.africa().count() == 0
    assert Country.objects.asia().count() == 0
    assert Country.objects.south_america().count() == 0
