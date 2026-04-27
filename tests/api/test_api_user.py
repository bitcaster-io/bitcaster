from typing import TYPE_CHECKING, Any, NamedTuple

import factory
import pytest
from rest_framework.test import APIClient

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
        ChannelFactory,
        EventFactory,
        UserRoleFactory,
    )

    event: Event = EventFactory.create(
        application__project__organization__name=org_name,
        application__project__name=prj_name,
        application__name=app_name,
        slug=event_slug,
    )
    # Grant FULL_ACCESS for API tests
    key = ApiKeyFactory.create(
        user=admin_user,
        grants=[Grant.FULL_ACCESS],
        application=None,
        project=event.application.project,
        organization=event.application.project.organization,
    )
    ch = ChannelFactory.create(project=event.application.project)
    role: "UserRole" = UserRoleFactory.create(organization__name=org_name, user__custom_fields={"custom": 1})
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


def test_user_list(client: APIClient, data: SampleData) -> None:
    url = f"/api/o/{data.org.slug}/u/"
    res = client.get(url)
    assert res.status_code == 200
    data: list[dict[str, Any]] = res.json()
    assert len(data) >= 1


def test_user_retrieve(client: APIClient, data: SampleData) -> None:
    url = f"/api/o/{data.org.slug}/u/{data.user.username}/"
    res = client.get(url)
    assert res.status_code == 200
    assert res.json()["id"] == data.user.pk


def test_user_messages(client: APIClient, data: SampleData) -> None:
    url = f"/api/o/{data.org.slug}/u/{data.user.username}/messages/"
    res = client.get(url)
    assert res.status_code == 200
    assert isinstance(res.json(), list)


def test_user_addresses(client: APIClient, data: SampleData) -> None:
    url = f"/api/o/{data.org.slug}/u/{data.user.username}/addresses/"
    res = client.get(url)
    assert res.status_code == 200


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


def test_user_update(client: APIClient, data: SampleData) -> None:
    # create new user and add to the organization
    url = f"/api/o/{data.org.slug}/u/{data.user.username}/"
    res = client.put(url, {"last_name": "aaaaaa"}, format="json")
    assert res.json()["last_name"] == "aaaaaa"
    assert data.org.users.filter(last_name="aaaaaa").exists()


def test_user_update_custom_fields(client: APIClient, data: SampleData) -> None:
    url = f"/api/o/{data.org.slug}/u/{data.user.username}/"
    res = client.put(url, {"custom_fields": {"f1": 1}}, format="json")
    assert res.status_code == 200
    assert not data.org.users.filter(custom_fields__f1=1).exists()


def test_user_update_custom_fields_add(client: APIClient, data: SampleData) -> None:
    url = f"/api/o/{data.org.slug}/u/{data.user.username}/"
    res = client.put(url, {"custom_fields": {"f1": 1}, "_mode": "merge"}, format="json")
    assert res.status_code == 200
    assert res.json()["custom_fields"] == {"custom": 1, "f1": 1}
    assert data.org.users.filter(custom_fields__f1=1, custom_fields__custom=1).exists()


def test_user_update_custom_fields_override(client: APIClient, data: SampleData) -> None:
    url = f"/api/o/{data.org.slug}/u/{data.user.username}/"
    res = client.put(url, {"custom_fields": {"custom": 2}, "_mode": "override"}, format="json")
    assert res.status_code == 200
    assert res.json()["custom_fields"] == {"custom": 2}
    assert data.org.users.filter(custom_fields__custom=2).exists()


def test_user_update_custom_fields_rewrite(client: APIClient, data: SampleData) -> None:
    url = f"/api/o/{data.org.slug}/u/{data.user.username}/"
    res = client.put(url, {"custom_fields": {"xx": 2}, "_mode": "rewrite"}, format="json")
    assert res.status_code == 200
    assert res.json()["custom_fields"] == {"xx": 2}
    assert data.org.users.exclude(custom_fields__has_key="custom").filter(custom_fields__xx=2).exists()


def test_user_update_custom_fields_remove(client: APIClient, data: SampleData) -> None:
    url = f"/api/o/{data.org.slug}/u/{data.user.username}/"
    res = client.put(url, {"custom_fields": {"custom": 2}, "_mode": "remove"}, format="json")
    assert res.status_code == 200
    assert res.json()["custom_fields"] == {}
    assert not data.org.users.filter(custom_fields__has_key="custom").exists()


def test_user_addresses_add(client: APIClient, data: SampleData) -> None:
    # create new user address
    new_email = "private@example.com"
    url = f"/api/o/{data.org.slug}/u/{data.user.username}/addresses/"
    res = client.post(url, {"value": new_email, "type": "email", "name": "private email"})
    assert res.json()
    assert data.user.addresses.filter(value=new_email).exists()


def test_user_addresses_add_invalid(client: APIClient, data: SampleData) -> None:
    # create new user address
    url = f"/api/o/{data.org.slug}/u/{data.user.username}/addresses/"
    res = client.post(url, {"value": "", "type": "email", "name": "private email"})
    assert res.status_code == 400
