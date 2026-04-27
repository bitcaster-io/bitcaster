from typing import TYPE_CHECKING, Any, NamedTuple

import factory
import pytest
from rest_framework.test import APIClient

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

org_name = "orgappe3"
prj_name = "prjappe3"


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

    event: Event = EventFactory.create(
        application__project__organization__name=org_name,
        application__project__organization__slug=org_name,
        application__project__name=prj_name,
        application__project__slug=prj_name,
    )
    app = event.application
    # Grant FULL_ACCESS to bypass scope checks in tests
    key = ApiKeyFactory.create(
        user=admin_user,
        grants=[Grant.FULL_ACCESS],
        application=app,  # Set application scope for retrieve
        project=event.application.project,
        organization=event.application.project.organization,
    )
    return SampleData(
        org=event.application.project.organization,
        prj=event.application.project,
        key=key,
    )


def test_application_list(client: APIClient, data: SampleData) -> None:
    """Test application list endpoint"""
    url = f"/api/o/{data.org.slug}/p/{data.prj.slug}/a/"
    res = client.get(url)
    assert res.status_code == 200
    results: list[dict[str, Any]] = res.json()
    assert len(results) >= 1


def test_application_retrieve(client: APIClient, data: SampleData) -> None:
    """Test application retrieve endpoint"""
    # Get the application from the project
    app = data.prj.applications.first()
    url = f"/api/o/{data.org.slug}/p/{data.prj.slug}/a/{app.slug}/"
    res = client.get(url)
    assert res.status_code == 200
    assert res.json()["slug"] == app.slug
