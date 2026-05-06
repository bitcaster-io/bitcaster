from typing import TYPE_CHECKING, Any, NamedTuple

import factory
from rest_framework.test import APIClient

import pytest
from testutils.perms import key_grants

from strategy_field.utils import fqn

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
    g = key_grants(data.key, Grant.FULL_ACCESS)
    g.start()
    c._key = data.key
    c.credentials(HTTP_AUTHORIZATION=f"Key {data.key.key}")
    yield c
    g.stop()


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
    key = ApiKeyFactory.create(
        user=admin_user, grants=[], application=None, project=None, organization=event.application.project.organization
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
    assert data == [
        {
            "name": org_channel.name,
            "dispatcher": fqn(org_channel.dispatcher),
            "locked": False,
            "protocol": org_channel.protocol,
        }
    ]
