import pytest

from geo.hierarchy import adm_italy, adm_usa, adm_uk


@pytest.mark.django_db
def test_italy(italy):
    adm_italy()


@pytest.mark.django_db
def test_usa(usa):
    adm_usa()


@pytest.mark.django_db
def test_uk(uk):
    uk, state, county, township, parish = adm_uk()

    assert parish.country == uk
    assert parish.parent == township
