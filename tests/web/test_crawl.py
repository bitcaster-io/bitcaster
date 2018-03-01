import pytest

pytestmark = pytest.mark.django_db


def test_index(django_app):
    "home is always accessible"
    res = django_app.get('/')
    assert res.html.find('title').text == "Bitcaster"
