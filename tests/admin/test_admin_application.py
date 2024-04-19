import pytest
from django.urls import reverse


@pytest.fixture()
def app(django_app_factory, db):
    from testutils.factories import SuperUserFactory

    django_app = django_app_factory(csrf_checks=False)
    admin_user = SuperUserFactory(username="superuser")
    django_app.set_user(admin_user)
    django_app._user = admin_user
    return django_app


@pytest.fixture()
def application(db):
    from testutils.factories import ApplicationFactory

    return ApplicationFactory()


@pytest.fixture()
def bitcaster(db):
    from testutils.factories import ApplicationFactory

    return ApplicationFactory(name="bitcaster")


def test_get_readonly_fields(app, application, bitcaster) -> None:
    url = reverse("admin:bitcaster_application_change", args=[application.pk])
    res = app.get(url)
    frm = res.forms["application_form"]
    assert "project" in frm.fields
    assert "name" in frm.fields

    url = reverse("admin:bitcaster_application_change", args=[bitcaster.pk])
    res = app.get(url)
    frm = res.forms["application_form"]
    assert "project" not in frm.fields
    assert "name" not in frm.fields
    assert "slug" not in frm.fields
