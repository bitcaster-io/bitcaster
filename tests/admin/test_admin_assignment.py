from typing import TYPE_CHECKING, TypedDict
from unittest import mock
from unittest.mock import Mock

import pytest
from django.urls import reverse
from django_webtest import DjangoTestApp

if TYPE_CHECKING:
    from webtest.response import TestResponse

    from bitcaster.models import Assignment, SocialProvider

    Context = TypedDict("Context", {"provider": SocialProvider})


@pytest.fixture()
def app(django_app_factory, admin_user) -> DjangoTestApp:
    django_app: DjangoTestApp = django_app_factory(csrf_checks=False)
    django_app.set_user(admin_user)
    django_app._user = admin_user
    return django_app


def test_edit(app: DjangoTestApp, assignment, settings) -> None:
    settings.ROOT_TOKEN_HEADER = "abc"
    settings.ROOT_TOKEN = "123"
    url = reverse("admin:bitcaster_assignment_change", args=[assignment.pk])

    res: "TestResponse" = app.get(f"{url}?user={app._user.pk}")
    assert res


def test_validate(app: DjangoTestApp, assignment: "Assignment", monkeypatch) -> None:

    url = reverse("admin:bitcaster_assignment_validate", args=[assignment.pk])
    monkeypatch.setattr("bitcaster.admin.assignment.AssignmentAdmin.message_user", collector := Mock())

    with mock.patch.object(type(assignment.channel.dispatcher), "need_subscription", True):
        app.get(url).follow()
    assert collector.call_count == 1
    assert collector.call_args_list[0].args[1:] == ("Cannot be validated.", 40)

    # with mock.patch.object(type(assignment.channel.dispatcher), "need_subscription", True):
    #     res: "TestResponse" = app.get(url).follow()
    # messages = list(res.context.get("messages"))
    # assert messages == [Message(level=40, message="Cannot be validated.")]
