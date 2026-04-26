from typing import TYPE_CHECKING, Any, NamedTuple

import factory
import pytest
from rest_framework.test import APIClient
from testutils.perms import key_grants

from bitcaster.auth.constants import Grant

if TYPE_CHECKING:
    from bitcaster.models import (
        ApiKey,
        Event,
        Organization,
        Project,
        User,
    )


class SampleData(NamedTuple):
    org: "Organization"
    prj: "Project"
    key: "ApiKey"


faker = factory.Faker._get_faker()

pytestmark = [pytest.mark.api, pytest.mark.django_db]

org_name = "orgproj2"
prj_name = "prjproj2"


@pytest.fixture
def client(data: SampleData):
    c = APIClient()
    c._key = data.key
    c.credentials(HTTP_AUTHORIZATION=f"Key {data.key.key}")
    return c


@pytest.fixture
def data(admin_user: "User", system_objects: Any) -> SampleData:
    from testutils.factories import (
        ApiKeyFactory,
        EventFactory,
    )

    event: "Event" = EventFactory.create(application__project__organization__name=org_name)
    key = ApiKeyFactory.create(
        user=admin_user, grants=[], application=None, project=None, organization=event.application.project.organization
    )
    return SampleData(
        org=event.application.project.organization,
        prj=event.application.project,
        key=key,
    )


def test_project_list(client: APIClient, data: SampleData) -> None:
    url = f"/api/o/{data.org.slug}/p/"
    res = client.get(url)
    assert res.status_code == 403

    with key_grants(data.key, [Grant.ORGANIZATION_READ], organization=data.org):
        res = client.get(url)
    assert res.status_code == 200
    results: list[dict[str, Any]] = res.json()
    assert len(results) >= 1
    assert any(p["slug"] == data.prj.slug for p in results)


def test_project_retrieve(client: APIClient, data: SampleData) -> None:
    url = f"/api/o/{data.org.slug}/p/{data.prj.slug}/"
    res = client.get(url)
    assert res.status_code == 403

    with key_grants(data.key, [Grant.ORGANIZATION_READ], project=data.prj, organization=data.org):
        res = client.get(url)
    assert res.status_code == 200
    assert res.json()["slug"] == data.prj.slug
