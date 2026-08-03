from typing import TYPE_CHECKING, Any

from rest_framework.test import APIClient

import pytest
from testutils.factories import (
    AddressFactory,
    ApiKeyFactory,
    AssignmentFactory,
    DistributionListFactory,
    EventFactory,
    UserFactory,
    UserRoleFactory,
)
from testutils.perms import key_grants

from bitcaster.auth.constants import Grant

if TYPE_CHECKING:
    from bitcaster.models import Address, ApiKey, Application, Assignment, DistributionList, Event, User

pytestmark = [pytest.mark.api, pytest.mark.django_db]

org_slug = "org-unreg"
prj_slug = "prj-unreg"
app_slug = "app-unreg"


@pytest.fixture
def data(admin_user: "User", system_objects: Any) -> dict[str, Any]:
    event: Event = EventFactory(
        application__project__organization__name=org_slug,
        application__project__name=prj_slug,
        application__name=app_slug,
        application__slug=app_slug,
    )
    app: Application = event.application
    other_event: Event = EventFactory(
        application__project__organization__name=org_slug,
        application__project__name=prj_slug,
    )
    other_app: Application = other_event.application

    user: "User" = UserFactory()
    UserRoleFactory(user=user, organization=app.project.organization)
    address: "Address" = AddressFactory(user=user, value=user.email)
    assignment: "Assignment" = AssignmentFactory(address=address)

    user2: "User" = UserFactory()
    UserRoleFactory(user=user2, organization=app.project.organization)
    address2: "Address" = AddressFactory(user=user2, value=user2.email)
    assignment2: "Assignment" = AssignmentFactory(address=address2)

    dl_pinned: DistributionList = DistributionListFactory(project=app.project, application=app, recipients=[assignment])
    dl_pinned_other_user: DistributionList = DistributionListFactory(
        project=app.project, application=app, recipients=[assignment2]
    )
    dl_not_pinned: DistributionList = DistributionListFactory(
        project=app.project, application=None, recipients=[assignment]
    )
    dl_other_app: DistributionList = DistributionListFactory(
        project=app.project, application=other_app, recipients=[assignment]
    )

    key: "ApiKey" = ApiKeyFactory(
        user=admin_user,
        grants=[],
        application=None,
        project=None,
        organization=app.project.organization,
    )

    return {
        "org": app.project.organization,
        "prj": app.project,
        "app": app,
        "user": user,
        "key": key,
        "dl_pinned": dl_pinned,
        "dl_pinned_other_user": dl_pinned_other_user,
        "dl_not_pinned": dl_not_pinned,
        "dl_other_app": dl_other_app,
    }


def test_unregister_requires_grant(data: dict[str, Any]) -> None:
    client = APIClient()
    client._key = data["key"]
    client.credentials(HTTP_AUTHORIZATION=f"Key {data['key'].key}")
    url = f"/api/o/{data['org'].slug}/p/{data['prj'].slug}/a/{data['app'].slug}/unregister/{data['user'].username}/"
    res = client.post(url)
    assert res.status_code == 403


def test_unregister_removes_user_from_pinned_dl(data: dict[str, Any]) -> None:
    client = APIClient()
    client._key = data["key"]
    client.credentials(HTTP_AUTHORIZATION=f"Key {data['key'].key}")
    url = f"/api/o/{data['org'].slug}/p/{data['prj'].slug}/a/{data['app'].slug}/unregister/{data['user'].username}/"

    with key_grants(
        data["key"],
        [Grant.MANAGE_APPLICATION_USERS],
        organization=data["org"],
        project=data["prj"],
        application=data["app"],
    ):
        res = client.post(url)

    assert res.status_code == 200
    assert res.json()["deleted"] == 1

    data["dl_pinned"].refresh_from_db()
    assert data["dl_pinned"].recipients.count() == 0


def test_unregister_ignores_non_pinned_dl(data: dict[str, Any]) -> None:
    client = APIClient()
    client._key = data["key"]
    client.credentials(HTTP_AUTHORIZATION=f"Key {data['key'].key}")
    url = f"/api/o/{data['org'].slug}/p/{data['prj'].slug}/a/{data['app'].slug}/unregister/{data['user'].username}/"

    with key_grants(
        data["key"],
        [Grant.MANAGE_APPLICATION_USERS],
        organization=data["org"],
        project=data["prj"],
        application=data["app"],
    ):
        client.post(url)

    data["dl_not_pinned"].refresh_from_db()
    assert data["dl_not_pinned"].recipients.count() == 1


def test_unregister_ignores_other_app_dl(data: dict[str, Any]) -> None:
    client = APIClient()
    client._key = data["key"]
    client.credentials(HTTP_AUTHORIZATION=f"Key {data['key'].key}")
    url = f"/api/o/{data['org'].slug}/p/{data['prj'].slug}/a/{data['app'].slug}/unregister/{data['user'].username}/"

    with key_grants(
        data["key"],
        [Grant.MANAGE_APPLICATION_USERS],
        organization=data["org"],
        project=data["prj"],
        application=data["app"],
    ):
        client.post(url)

    data["dl_other_app"].refresh_from_db()
    assert data["dl_other_app"].recipients.count() == 1


def test_unregister_no_error_when_user_not_in_any_dl(data: dict[str, Any]) -> None:
    client = APIClient()
    client._key = data["key"]
    client.credentials(HTTP_AUTHORIZATION=f"Key {data['key'].key}")
    unknown_user: "User" = UserFactory()
    UserRoleFactory(user=unknown_user, organization=data["org"])
    url = f"/api/o/{data['org'].slug}/p/{data['prj'].slug}/a/{data['app'].slug}/unregister/{unknown_user.username}/"

    with key_grants(
        data["key"],
        [Grant.MANAGE_APPLICATION_USERS],
        organization=data["org"],
        project=data["prj"],
        application=data["app"],
    ):
        res = client.post(url)

    assert res.status_code == 200
    assert res.json()["deleted"] == 0


def test_unregister_uses_post_verb(data: dict[str, Any]) -> None:
    client = APIClient()
    client._key = data["key"]
    client.credentials(HTTP_AUTHORIZATION=f"Key {data['key'].key}")
    url = f"/api/o/{data['org'].slug}/p/{data['prj'].slug}/a/{data['app'].slug}/unregister/{data['user'].username}/"

    with key_grants(
        data["key"],
        [Grant.MANAGE_APPLICATION_USERS],
        organization=data["org"],
        project=data["prj"],
        application=data["app"],
    ):
        res_get = client.get(url)
        res_post = client.post(url)

    assert res_get.status_code == 405
    assert res_post.status_code == 200
