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


# @pytest.fixture()
# def project(db):
#     from testutils.factories import ProjectFactory
#
#     return ProjectFactory()
#

# @pytest.fixture()
# def bitcaster(db):
#     from testutils.factories import ProjectFactory
#
#     return ProjectFactory(name=Bitcaster.PROJECT, organization__name=Bitcaster.ORGANIZATION)

#
# @pytest.fixture()
# def organization(db):
#
#     from testutils.factories.org import OrganizationFactory
#
#     return OrganizationFactory()


def test_get_readonly_fields(app, project, bitcaster) -> None:
    url = reverse("admin:bitcaster_project_change", args=[project.pk])
    res = app.get(url)
    frm = res.forms["project_form"]
    assert "organization" in frm.fields
    assert "name" in frm.fields

    url = reverse("admin:bitcaster_project_change", args=[bitcaster.project.pk])
    res = app.get(url)
    frm = res.forms["project_form"]
    assert "organization" not in frm.fields
    assert "name" not in frm.fields
    assert "slug" not in frm.fields


def test_add(app, organization, bitcaster) -> None:
    url = reverse("admin:bitcaster_project_add")
    res = app.get(url)
    frm = res.forms["project_form"]
    frm["name"] = "dummy"
    frm["organization"].force_value(organization.pk)
    frm["owner"].force_value(organization.owner.pk)
    frm["environments"].force_value("development,production")
    res = frm.submit("Save and continue editing")
    assert res.status_code == 302, res.context["adminform"].errors
