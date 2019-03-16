import pytest

from bitcaster.models import Team

pytestmark = pytest.mark.django_db


def test_str(team1):
    assert str(team1)


def test_recipient(subscription1):
    assert str(subscription1.recipient)


@pytest.mark.django_db
def test_create_slug(application1, user1):
    app = Team(application=application1, slug='abc', manager=user1)
    app.save()
    assert app.slug == 'abc'


@pytest.mark.django_db
def test_create_no_slug(application1, user1):
    app = Team(application=application1, slug='', manager=user1)
    app.save()
    assert app.slug
