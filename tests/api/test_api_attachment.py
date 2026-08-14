from typing import TYPE_CHECKING, Any, TypedDict

import uuid

from rest_framework import status
from rest_framework.test import APIClient

import pytest
from testutils.perms import key_grants

from django.core.files.uploadedfile import SimpleUploadedFile

from bitcaster.auth.constants import Grant
from bitcaster.models import Attachment

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

org_slug = "org1"
prj_slug = "prj1"
app_slug = "app1"
event_slug = "evt1"
dl_pk = 999


@pytest.fixture
def client(data: "Context"):
    client = APIClient()
    grant_context = key_grants(
        data["key"],
        [Grant.APPLICATION_ADMIN],
        organization=data["org"],
        project=data["prj"],
        application=data["app"],
    )
    grant_context.start()
    client.credentials(HTTP_AUTHORIZATION=f"Key {data['key'].key}")
    yield client
    grant_context.stop()


@pytest.fixture
def data(user: "User", system_objects: Any) -> "Context":
    from testutils.factories import (
        ApiKeyFactory,
        ApplicationFactory,
        AssignmentFactory,
        ChannelFactory,
        DistributionListFactory,
        EventFactory,
    )

    app = ApplicationFactory(
        slug=app_slug,
        project__slug=prj_slug,
        project__organization__slug=org_slug,
        advanced_configuration={"support_attachment": True},
    )
    event: Event = EventFactory.create(application=app, slug=event_slug)
    key = ApiKeyFactory.create(
        user=user, grants=[], application=None, project=None, organization=event.application.project.organization
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
        "user": user,
        "ch": ch,
    }


@pytest.fixture
def uploaded_file():
    return SimpleUploadedFile("test.txt", b"Test text file", content_type="text/plain")


@pytest.fixture
def updated_file():
    return SimpleUploadedFile("updated.txt", b"Updated text file", content_type="text/plain")


def _base_url():
    return f"/api/o/{org_slug}/p/{prj_slug}/a/{app_slug}/attachment/"


def test_updated_file_upload_generates_correlation_id(
    client: APIClient, data: "Context", uploaded_file: SimpleUploadedFile
):
    with key_grants(
        data["key"],
        [Grant.APPLICATION_ADMIN],
        organization=data["org"],
        project=data["prj"],
        application=data["app"],
    ):
        response = client.post(_base_url(), data={"document": uploaded_file}, format="multipart")
        assert response.status_code == status.HTTP_201_CREATED

        response_json = response.json()
        attachment = Attachment.objects.get(application=data["app"], correlation_id=response_json["correlation_id"])

        # we didn't give a correlation id - was it created correctly
        # as a UUID?
        assert uuid.UUID(attachment.correlation_id).version == 4
        assert attachment.document.read() == b"Test text file"
        assert attachment.mime_type == "text/plain"
        assert attachment.size == 14

        assert response_json == {
            "correlation_id": attachment.correlation_id,
            "filename": attachment.filename,
            "mime_type": attachment.mime_type,
            "size": attachment.size,
        }


def test_post_updated_file_with_provided_correlation_id(
    client: APIClient, data: "Context", uploaded_file: SimpleUploadedFile
):
    correlation_id = "test-correlation-id"
    url = f"{_base_url()}{correlation_id}/"

    with key_grants(
        data["key"],
        [Grant.APPLICATION_ADMIN],
        organization=data["org"],
        project=data["prj"],
        application=data["app"],
    ):
        response = client.post(url, data={"document": uploaded_file}, format="multipart")
        assert response.status_code == status.HTTP_201_CREATED
        attachment = Attachment.objects.get(application=data["app"], correlation_id=correlation_id)

        assert attachment.correlation_id == correlation_id
        assert attachment.document.read() == b"Test text file"
        assert attachment.mime_type == uploaded_file.content_type
        assert attachment.size == 14

        assert response.json() == {
            "correlation_id": attachment.correlation_id,
            "filename": attachment.filename,
            "mime_type": attachment.mime_type,
            "size": attachment.size,
        }


def test_post_duplicate_correlation_id_returns_conflict(
    client: APIClient, data: "Context", uploaded_file: SimpleUploadedFile
):
    correlation_id = "test-correlation-id"
    url = f"{_base_url()}{correlation_id}/"

    with key_grants(
        data["key"],
        [Grant.APPLICATION_ADMIN],
        organization=data["org"],
        project=data["prj"],
        application=data["app"],
    ):
        client.post(url, data={"document": uploaded_file}, format="multipart")

        response = client.post(url, data={"document": uploaded_file}, format="multipart")
        assert response.status_code == status.HTTP_409_CONFLICT


def test_post_attachment_without_support_returns_bad_response(
    client: APIClient, data: "Context", uploaded_file: SimpleUploadedFile
):
    data["app"].advanced_configuration["support_attachment"] = False
    data["app"].save()

    with key_grants(
        data["key"],
        [Grant.APPLICATION_ADMIN],
        organization=data["org"],
        project=data["prj"],
        application=data["app"],
    ):
        response = client.post(_base_url(), data={"document": uploaded_file}, format="multipart")
        assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_put_updates_existing_file(
    client: APIClient, data: "Context", uploaded_file: SimpleUploadedFile, updated_file: SimpleUploadedFile
):
    correlation_id = "test-correlation-id"
    url = f"{_base_url()}{correlation_id}/"

    with key_grants(
        data["key"],
        [Grant.APPLICATION_ADMIN],
        organization=data["org"],
        project=data["prj"],
        application=data["app"],
    ):
        client.post(url, data={"document": uploaded_file}, format="multipart")

        response = client.put(url, data={"document": updated_file}, format="multipart")
        assert response.status_code == status.HTTP_200_OK


def test_put_non_existing_correlation_id_returns_not_found(
    client: APIClient, data: "Context", uploaded_file: SimpleUploadedFile
):
    correlation_id = "test-correlation-id"
    url = f"{_base_url()}{correlation_id}/"

    with key_grants(
        data["key"],
        [Grant.APPLICATION_ADMIN],
        organization=data["org"],
        project=data["prj"],
        application=data["app"],
    ):
        response = client.put(url, data={"document": uploaded_file}, format="multipart")
        assert response.status_code == status.HTTP_404_NOT_FOUND


def test_put_attachment_without_support_returns_bad_response(
    client: APIClient, data: "Context", uploaded_file: SimpleUploadedFile, updated_file: SimpleUploadedFile
):
    with key_grants(
        data["key"],
        [Grant.APPLICATION_ADMIN],
        organization=data["org"],
        project=data["prj"],
        application=data["app"],
    ):
        client.post(_base_url(), data={"document": uploaded_file}, format="multipart")

    data["app"].advanced_configuration["support_attachment"] = False
    data["app"].save()

    with key_grants(
        data["key"],
        [Grant.APPLICATION_ADMIN],
        organization=data["org"],
        project=data["prj"],
        application=data["app"],
    ):
        response = client.put(_base_url(), data={"document": updated_file}, format="multipart")
        assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_attachment_list(
    client: APIClient, data: "Context", uploaded_file: SimpleUploadedFile, updated_file: SimpleUploadedFile
):
    url = _base_url()

    post_response_1 = client.post(url, data={"document": uploaded_file}, format="multipart")
    post_response_2 = client.post(url, data={"document": updated_file}, format="multipart")

    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK

    correlation_id_1 = post_response_1.json().get("correlation_id")
    attachment_1 = Attachment.objects.get(application=data["app"], correlation_id=correlation_id_1)
    expected_attachment_json_1 = {
        "correlation_id": attachment_1.correlation_id,
        "filename": attachment_1.filename,
        "mime_type": attachment_1.mime_type,
        "size": attachment_1.size,
    }

    correlation_id_2 = post_response_2.json().get("correlation_id")
    attachment_2 = Attachment.objects.get(application=data["app"], correlation_id=correlation_id_2)
    expected_attachment_json_2 = {
        "correlation_id": attachment_2.correlation_id,
        "filename": attachment_2.filename,
        "mime_type": attachment_2.mime_type,
        "size": attachment_2.size,
    }

    assert isinstance(response.json(), list)
    assert sorted(response.json(), key=lambda j: j["correlation_id"]) == sorted(
        [expected_attachment_json_1, expected_attachment_json_2], key=lambda j: j["correlation_id"]
    )


def test_attachment_denied_without_admin_grant(client: APIClient, data: "Context", uploaded_file: SimpleUploadedFile):
    with key_grants(data["key"], [], add=False, organization=data["org"], project=data["prj"], application=data["app"]):
        response = client.post(_base_url(), data={"document": uploaded_file}, format="multipart")
        assert response.status_code == status.HTTP_403_FORBIDDEN
