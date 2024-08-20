from typing import TYPE_CHECKING, Any, NamedTuple

import factory
import pytest
from rest_framework.test import APIClient
from testutils.factories import (
    AddressFactory,
    ApiKeyFactory,
    ChannelFactory,
    EventFactory,
    UserRoleFactory,
)
from testutils.perms import key_grants

from bitcaster.auth.constants import Grant

if TYPE_CHECKING:
    from bitcaster.models import (
        ApiKey,
        Application,
        Channel,
        Event,
        Organization,
        Project,
        User,
        UserRole,
    )


class SampleData(NamedTuple):
    org: "Organization"
    prj: "Project"
    app: "Application"
    event: "Event"
    key: "ApiKey"
    user: "User"
    ch: "Channel"


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
    c._key = data.key
    c.credentials(HTTP_AUTHORIZATION=f"Key {data.key.key}")
    yield c
    g.stop()


@pytest.fixture()
def data(admin_user: "User", system_objects: Any) -> SampleData:

    event: Event = EventFactory(
        application__project__organization__name=org_name,
        application__project__name=prj_name,
        application__name=app_name,
        slug=event_slug,
    )
    key = ApiKeyFactory(
        user=admin_user, grants=[], application=None, project=None, organization=event.application.project.organization
    )
    ch = ChannelFactory(project=event.application.project)
    role: "UserRole" = UserRoleFactory(organization__name=org_name)
    AddressFactory(user=role.user, value=role.user.email)
    return SampleData(
        org=event.application.project.organization,
        prj=event.application.project,
        app=event.application,
        event=event,
        key=key,
        user=role.user,
        ch=ch,
    )


def test_org_detail(client: APIClient) -> None:
    url = f"/api/o/{client._key.organization.slug}/"
    res = client.get(url)
    data: dict[str, str] = res.json()
    with key_grants(client._key, [Grant.ORGANIZATION_READ]):
        client._key.refresh_from_db()
        assert data["slug"] == client._key.organization.slug


def test_org_channels(client: APIClient, org_channel: "Channel") -> None:
    # list organization channels
    url = f"/api/o/{org_channel.organization.slug}/c/"
    with key_grants(client._key, [Grant.ORGANIZATION_READ], organization=org_channel.organization):
        res = client.get(url)
    data: list[dict[str, Any]] = res.json()
    assert data == [{"name": org_channel.name, "protocol": org_channel.protocol}]


def test_user_list(client: APIClient, org_user: "User") -> None:
    org: Organization = org_user.organizations.first()
    url = f"/api/o/{org.slug}/u/"
    with key_grants(client._key, [Grant.ORGANIZATION_READ], organization=org):
        res = client.get(url)
    data: list[dict[str, Any]] = res.json()
    ids = [e["id"] for e in data]
    assert ids == [org_user.pk]


def test_user_add_existing(client: APIClient, data: SampleData, user: "User") -> None:
    # add exiting user to the organization
    url = f"/api/o/{data.org.slug}/u/"
    res = client.post(url, {"email": user.email})
    return_value: dict[str, Any] = res.json()
    assert return_value["id"] == user.pk


def test_user_create(client: APIClient, data: SampleData) -> None:
    # create new user and add to the organization
    email = faker.email()
    url = f"/api/o/{data.org.slug}/u/"
    res = client.post(url, {"email": email})
    assert res.json()["email"] == email
    assert data.org.users.filter(email=email).exists()
    # assert User.objects.filter(email=email).exists()


def test_user_update(client: APIClient, data: SampleData) -> None:
    # create new user and add to the organization
    url = f"/api/o/{data.org.slug}/u/{data.user.username}/"
    res = client.put(url, {"last_name": "aaaaaa"})
    assert res.json()["last_name"] == "aaaaaa"
    assert data.org.users.filter(last_name="aaaaaa").exists()


def test_user_update_invalid(client: APIClient, data: SampleData) -> None:
    # create new user and add to the organization
    url = f"/api/o/{data.org.slug}/u/{data.user.username}/"
    res = client.put(url, {"email": "--"})
    assert res.status_code == 400


def test_user_addresses(client: APIClient, data: SampleData) -> None:
    # list user addresses
    url = f"/api/o/{data.org.slug}/u/{data.user.username}/address/"
    res = client.get(url)
    assert res.json()


def test_user_addresses_add(client: APIClient, data: SampleData) -> None:
    # create new user address
    new_email = "private@example.com"
    url = f"/api/o/{data.org.slug}/u/{data.user.username}/address/"
    res = client.post(url, {"value": new_email, "type": "email", "name": "private email"})
    assert res.json()
    assert data.user.addresses.filter(value=new_email).exists()


def test_user_addresses_add_invalid(client: APIClient, data: SampleData) -> None:
    # create new user address
    url = f"/api/o/{data.org.slug}/u/{data.user.username}/address/"
    res = client.post(url, {"value": "", "type": "email", "name": "private email"})
    assert res.status_code == 400
