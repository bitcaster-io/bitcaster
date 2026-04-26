import json
from typing import TYPE_CHECKING, Any, NamedTuple

import factory
import pytest
from rest_framework.test import APIClient
from testutils.perms import key_grants

from bitcaster.auth.constants import Grant

if TYPE_CHECKING:
    from bitcaster.models import (
        Address,
        ApiKey,
        Assignment,
        DistributionList,
        Event,
        Organization,
        Project,
        User,
        UserRole,
    )


class SampleData(NamedTuple):
    org: "Organization"
    prj: "Project"
    key: "ApiKey"
    dl: "DistributionList"
    asm: "Assignment"


faker = factory.Faker._get_faker()

pytestmark = [pytest.mark.api, pytest.mark.django_db]

# WE DO NOT USE REVERSE HERE. WE NEED TO CHECK ENDPOINTS CONTRACTS

org_name = "orglist2"
prj_name = "prjlist2"
app_name = "applist2"
event_slug = "evtlist2"


@pytest.fixture
def client(data: SampleData):
    c = APIClient()
    c._key = data.key
    c.credentials(HTTP_AUTHORIZATION=f"Key {data.key.key}")
    return c


@pytest.fixture
def data(admin_user: "User", system_objects: Any) -> SampleData:
    from testutils.factories import (
        AddressFactory,
        ApiKeyFactory,
        AssignmentFactory,
        DistributionListFactory,
        EventFactory,
        UserRoleFactory,
    )

    event: Event = EventFactory.create(
        application__project__organization__name=org_name,
        application__project__name=prj_name,
        application__name=app_name,
        slug=event_slug,
    )
    key = ApiKeyFactory.create(
        user=admin_user, grants=[], application=None, project=None, organization=event.application.project.organization
    )
    role: "UserRole" = UserRoleFactory.create(organization__name=org_name)
    address: "Address" = AddressFactory.create(user=role.user, value=role.user.email)
    asm: "Assignment" = AssignmentFactory.create(address=address)

    distribution_list = DistributionListFactory.create(project=event.application.project, recipients=[asm])
    return SampleData(
        org=event.application.project.organization,
        prj=event.application.project,
        key=key,
        dl=distribution_list,
        asm=asm,
    )


def test_distribution_list(client: APIClient, data: SampleData) -> None:
    url = f"/api/o/{data.org.slug}/p/{data.prj.slug}/d/"
    res = client.get(url)
    assert res.status_code == 403

    with key_grants(data.key, [Grant.DISTRIBUTION_LIST], project=data.prj, organization=data.org):
        res = client.get(url)
        distribution_lists = res.json()
    assert distribution_lists[0]["name"] == data.dl.name


def test_distribution_members(client: APIClient, data: SampleData) -> None:
    """Test distribution list members endpoint"""
    members_url = f"/api/o/{data.org.slug}/p/{data.prj.slug}/d/{data.dl.pk}/m/"
    res = client.get(members_url)
    assert res.status_code == 403

    with key_grants(data.key, [Grant.DISTRIBUTION_LIST], project=data.prj, organization=data.org):
        res = client.get(members_url)
    assert res.status_code == 200


def test_distribution_create(client: APIClient, data: SampleData) -> None:
    from bitcaster.models import DistributionList

    url = f"/api/o/{data.org.slug}/p/{data.prj.slug}/d/"
    res = client.post(url, {"name": "Sample List #1"})
    assert res.status_code == 403

    with key_grants(data.key, [Grant.DISTRIBUTION_LIST], project=data.prj, organization=data.org):
        res = client.post(url, {"name": "Sample List #1"})
    assert res.status_code == 201
    assert DistributionList.objects.filter(name="Sample List #1").exists()


def test_distribution_create_duplicate(client: APIClient, data: SampleData) -> None:
    url = f"/api/o/{data.org.slug}/p/{data.prj.slug}/d/"
    res = client.post(url, {"name": data.dl.name})
    assert res.status_code == 403

    with key_grants(data.key, [Grant.DISTRIBUTION_LIST], project=data.prj, organization=data.org):
        res = client.post(url, {"name": data.dl.name})
    assert res.status_code == 400


def test_distribution_retrieve(client: APIClient, data: SampleData) -> None:
    """Test distribution list retrieve endpoint"""
    url = f"/api/o/{data.org.slug}/p/{data.prj.slug}/d/{data.dl.pk}/"
    res = client.get(url)
    assert res.status_code == 403

    with key_grants(data.key, [Grant.DISTRIBUTION_LIST], project=data.prj, organization=data.org):
        res = client.get(url)
    assert res.status_code == 200
    assert res.json()["name"] == data.dl.name


def test_distribution_add_recipient(client: APIClient, data: SampleData) -> None:
    url = f"/api/o/{data.org.slug}/p/{data.prj.slug}/d/{data.dl.pk}/add/"
    res = client.post(url, [data.asm.address.value], format="json")
    assert res.status_code == 403

    with key_grants(data.key, [Grant.DISTRIBUTION_LIST], project=data.prj, organization=data.org):
        res = client.post(url, [data.asm.address.value], format="json")
    assert res.status_code == 200, res.json()
    data.dl.refresh_from_db()
    assert data.dl.recipients.filter(address__value=data.asm.address.value).exists()


def test_distribution_add_recipient_error(client: APIClient, data: SampleData) -> None:
    url = f"/api/o/{data.org.slug}/p/{data.prj.slug}/d/{data.dl.pk}/add/"
    res = client.post(url, json.dumps(["not-existent"]), format="json")
    assert res.status_code == 403

    with key_grants(data.key, [Grant.DISTRIBUTION_LIST], project=data.prj, organization=data.org):
        res = client.post(url, json.dumps(["not-existent"]), format="json")
    assert res.status_code == 400
