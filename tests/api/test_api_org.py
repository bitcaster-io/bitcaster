from typing import TYPE_CHECKING, TypedDict

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from testutils.factories.event import EventFactory
from testutils.factories.key import ApiKeyFactory

if TYPE_CHECKING:
    from bitcaster.models import ApiKey, Application, Event, Organization, Project, User

    Context = TypedDict(
        "Context",
        {
            "org": Organization,
            "prj": Project,
            "app": Application,
            "event": Event,
            "key": ApiKey,
            "user": User,
        },
    )

pytestmark = [pytest.mark.api, pytest.mark.django_db]

# WE DO NOT USE REVERSE HERE. WE NEED TO CHECK ENDPOINTS CONTRACTS

org_slug = "org1"
prj_slug = "prj1"
app_slug = "app1"


@pytest.fixture()
def client(admin_user) -> APIClient:
    c = APIClient()
    c.force_authenticate(admin_user)
    return c


@pytest.fixture()
def data(admin_user) -> "Context":

    event: Event = EventFactory(
        application__project__organization__slug=org_slug,
        application__project__slug=prj_slug,
        application__slug=app_slug,
    )
    key = ApiKeyFactory(user=admin_user, grants=[], application=event.application)
    return {
        "org": event.application.project.organization,
        "prj": event.application.project,
        "app": event.application,
        "event": event,
        "key": key,
        "user": admin_user,
    }


def pytest_generate_tests(metafunc):
    if "url" in metafunc.fixturenames:
        m = []
        for url in [
            "/api/organization/",
            f"/api/organization/{org_slug}/",
            f"/api/organization/{org_slug}/projects/",
            f"/api/organization/{org_slug}/projects/{prj_slug}/",
            f"/api/organization/{org_slug}/projects/{prj_slug}/applications/",
            f"/api/organization/{org_slug}/projects/{prj_slug}/applications/{app_slug}/",
            f"/api/organization/{org_slug}/projects/{prj_slug}/applications/{app_slug}/events/",
        ]:
            m.append(url)
        metafunc.parametrize("url", m, ids=m)


def test_security(client: APIClient, data: "Context", url) -> None:
    res = client.get(url, data={})
    assert res.status_code == status.HTTP_200_OK, url

    # client.credentials(HTTP_AUTHORIZATION=f"ApiKey {api_key.key}")
    # res = client.post(url, data={})
    # assert res.status_code == status.HTTP_403_FORBIDDEN
    # with key_grants(api_key, Grant.EVENT_TRIGGER):
    #     res = client.post(url, data={})
    #     assert res.status_code == status.HTTP_200_OK
