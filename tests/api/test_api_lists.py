import json
from typing import NamedTuple

import factory
import pytest
from rest_framework.test import APIClient
from testutils.factories import (
    AddressFactory,
    ApiKeyFactory,
    AssignmentFactory,
    DistributionListFactory,
    EventFactory,
    UserRoleFactory,
)
from testutils.perms import key_grants

from bitcaster.auth.constants import Grant
from bitcaster.models import (
    Address,
    ApiKey,
    Assignment,
    DistributionList,
    Event,
    Organization,
    Project,
    UserRole,
)

# if TYPE_CHECKING:


class SampleData(NamedTuple):
    org: "Organization"
    prj: "Project"
    key: "ApiKey"
    dl: "DistributionList"
    asm: "Assignment"


faker = factory.Faker._get_faker()

pytestmark = [pytest.mark.api, pytest.mark.django_db]

# WE DO NOT USE REVERSE HERE. WE NEED TO CHECK ENDPOINTS CONTRACTS

org_name = "org1"
prj_name = "prj1"
app_name = "app1"
event_slug = "evt1"


@pytest.fixture()
def client(data: SampleData) -> APIClient:
    c = APIClient()
    g = key_grants(data.key, Grant.FULL_ACCESS)
    g.start()
    c.credentials(HTTP_AUTHORIZATION=f"Key {data.key.key}")
    yield c
    g.stop()


@pytest.fixture()
def data(admin_user, system_objects) -> SampleData:

    event: Event = EventFactory(
        application__project__organization__name=org_name,
        application__project__name=prj_name,
        application__name=app_name,
        slug=event_slug,
    )
    key = ApiKeyFactory(
        user=admin_user, grants=[], application=None, project=None, organization=event.application.project.organization
    )
    # ch = ChannelFactory(project=event.application.project)
    role: "UserRole" = UserRoleFactory(organization__name=org_name)
    address: "Address" = AddressFactory(user=role.user, value=role.user.email)
    asm: "Assignment" = AssignmentFactory(address=address)

    distribution_list = DistributionListFactory(project=event.application.project, recipients=[asm])
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
    assert res.json() == [{"id": data.dl.pk, "name": data.dl.name}]


def test_distribution_create(client: APIClient, data: SampleData) -> None:
    url = f"/api/o/{data.org.slug}/p/{data.prj.slug}/d/"
    res = client.post(url, {"name": "Sample List #1"})
    assert res.status_code == 201
    assert DistributionList.objects.filter(name="Sample List #1").exists()


def test_distribution_create_duplicate(client: APIClient, data: SampleData) -> None:
    url = f"/api/o/{data.org.slug}/p/{data.prj.slug}/d/"
    res = client.post(url, {"name": data.dl.name})
    assert res.status_code == 400


def test_distribution_add_recipient(client: APIClient, data: SampleData) -> None:
    url = f"/api/o/{data.org.slug}/p/{data.prj.slug}/d/{data.dl.pk}/add/"
    res = client.post(url, [data.asm.address.value], format="json")
    assert res.status_code == 200, res.json()
    data.dl.refresh_from_db()
    assert data.dl.recipients.filter(address__value=data.asm.address.value).exists()


def test_distribution_add_recipient_error(client: APIClient, data: SampleData) -> None:
    url = f"/api/o/{data.org.slug}/p/{data.prj.slug}/d/{data.dl.pk}/add/"
    res = client.post(url, json.dumps(["not-existent"]), format="json")
    assert res.status_code == 400
