from typing import TYPE_CHECKING, Any, TypedDict

from rest_framework import status
from rest_framework.test import APIClient

import pytest
from testutils.perms import key_grants

from django.urls import ResolverMatch, resolve

from bitcaster.auth.constants import Grant

if TYPE_CHECKING:
    from bitcaster.models import (
        ApiKey,
        Application,
        Channel,
        DistributionList,
        Event,
        Organization,
        Project,
        User,
    )

    Context = TypedDict(
        "Context",
        {
            "org": Organization,
            "prj": Project,
            "app": Application,
            "event": Event,
            "dl": DistributionList,
            "key": ApiKey,
            "user": User,
            "ch": Channel,
        },
    )

pytestmark = [pytest.mark.api, pytest.mark.django_db]

# WE DO NOT USE REVERSE HERE. WE NEED TO CHECK ENDPOINTS CONTRACTS

org_slug = "org1"
prj_slug = "prj1"
app_slug = "app1"
event_slug = "evt1"
dl_pk = 999


@pytest.fixture
def client(data: "Context") -> APIClient:
    c = APIClient()
    g = key_grants(data["key"], Grant.FULL_ACCESS)
    g.start()
    c._key = data["key"]
    c.credentials(HTTP_AUTHORIZATION=f"Key {data['key'].key}")
    yield c
    g.stop()


@pytest.fixture
def data(admin_user: "User", system_objects: Any) -> "Context":
    from testutils.factories import (
        ApiKeyFactory,
        AssignmentFactory,
        ChannelFactory,
        DistributionListFactory,
        EventFactory,
    )

    event: Event = EventFactory.create(
        application__project__organization__slug=org_slug,
        application__project__slug=prj_slug,
        application__slug=app_slug,
        slug=event_slug,
    )
    key = ApiKeyFactory.create(
        user=admin_user, grants=[], application=None, project=None, organization=event.application.project.organization
    )
    ch = ChannelFactory.create(project=event.application.project)
    dl = DistributionListFactory.create(id=dl_pk, project=event.application.project, recipients=[AssignmentFactory()])
    return {
        "org": event.application.project.organization,
        "prj": event.application.project,
        "app": event.application,
        "event": event,
        "dl": dl,
        "key": key,
        "user": admin_user,
        "ch": ch,
    }


def pytest_generate_tests(metafunc: pytest.Metafunc) -> None:
    if "url" in metafunc.fixturenames:
        m = []
        ids = []
        for url in [
            f"/api/o/{org_slug}/",
            f"/api/o/{org_slug}/u/",  # users
            f"/api/o/{org_slug}/p/{prj_slug}/",
            f"/api/o/{org_slug}/p/{prj_slug}/d/",  # distributionlist
            f"/api/o/{org_slug}/p/{prj_slug}/d/{dl_pk}/m/",  # distributionlist members
            f"/api/o/{org_slug}/p/{prj_slug}/a/",  # applications
            f"/api/o/{org_slug}/p/{prj_slug}/c/",  # channels
            f"/api/o/{org_slug}/p/{prj_slug}/a/{app_slug}/e/",
        ]:
            m.append(url)
            r: ResolverMatch = resolve(url)
            ids.append(r.func.__name__)
        metafunc.parametrize("url", m, ids=ids)


def test_urls(client: APIClient, data: "Context", url: str) -> None:
    with key_grants(client._key, [], organization=data["org"], project=data["prj"], application=data["app"]):
        res = client.get(url, data={})
        assert res.status_code == status.HTTP_200_OK, url
