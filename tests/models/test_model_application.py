import pytest

from bitcaster.models import Application
from bitcaster.utils.tests.factories import ApplicationFactory


def test_application():
    app = Application(name='App1')
    assert str(app)


@pytest.mark.django_db
def test_application_channels(channel1):
    assert channel1.application.channels


@pytest.mark.django_db
def test_application_create():
    assert ApplicationFactory()


@pytest.mark.django_db
def test_application_create_slug(organization1):
    app = Application(organization=organization1, slug='abc')
    app.save()
    assert app.slug == 'abc'


@pytest.mark.django_db
def test_application_admins(application1):
    assert list(application1.admins) == []


@pytest.mark.django_db
def test_application_owners(application1):
    assert application1.owners
