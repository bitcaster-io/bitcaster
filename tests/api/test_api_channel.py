from typing import TYPE_CHECKING, Any, NamedTuple

import factory
from rest_framework.test import APIClient

import pytest
from testutils.perms import key_grants

from bitcaster.auth.constants import Grant

if TYPE_CHECKING:
    from bitcaster.models import (
        ApiKey,
        Channel,
        Organization,
        Project,
        User,
    )


class SampleData(NamedTuple):
    org: "Organization"
    prj: "Project"
    ch: "Channel"
    key: "ApiKey"


faker = factory.Faker._get_faker()

pytestmark = [pytest.mark.api, pytest.mark.django_db]

org_name = "orgch2"
prj_name = "prjch2"


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
        ChannelFactory,
    )

    ch = ChannelFactory.create(project__organization__name=org_name, project__name=prj_name)
    key = ApiKeyFactory.create(
        user=admin_user, grants=[], application=None, project=None, organization=ch.project.organization
    )
    return SampleData(
        org=ch.project.organization,
        prj=ch.project,
        ch=ch,
        key=key,
    )


def test_channel_list_for_org(client: APIClient, data: SampleData) -> None:
    url = f"/api/o/{data.org.slug}/c/"
    res = client.get(url)
    assert res.status_code == 403

    with key_grants(data.key, [Grant.ORGANIZATION_READ], organization=data.org):
        res = client.get(url)
    assert res.status_code == 200
    results: list[dict[str, Any]] = res.json()
    assert len(results) >= 1
    assert any(c["name"] == data.ch.name for c in results)


def test_channel_list_for_project(client: APIClient, data: SampleData) -> None:
    url = f"/api/o/{data.org.slug}/p/{data.prj.slug}/c/"
    res = client.get(url)
    assert res.status_code == 403

    with key_grants(data.key, [Grant.ORGANIZATION_READ], project=data.prj, organization=data.org):
        res = client.get(url)
    assert res.status_code == 200
    results: list[dict[str, Any]] = res.json()
    assert len(results) >= 1
    assert results[0]["name"] == data.ch.name


def test_channel_retrieve(client: APIClient, data: SampleData) -> None:
    url = f"/api/o/{data.org.slug}/p/{data.prj.slug}/c/{data.ch.pk}/"
    res = client.get(url)
    assert res.status_code == 403

    with key_grants(data.key, [Grant.ORGANIZATION_READ], project=data.prj, organization=data.org):
        res = client.get(url)
    assert res.status_code == 200
    assert res.json()["name"] == data.ch.name
