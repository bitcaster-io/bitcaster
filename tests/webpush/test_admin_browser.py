from typing import TYPE_CHECKING, TypedDict

import pytest
from django.urls import reverse
from django_webtest import DjangoTestApp
from django_webtest.pytest_plugin import MixinWithInstanceVariables

if TYPE_CHECKING:
    from bitcaster.models import Assignment, SocialProvider, User

    Context = TypedDict("Context", {"provider": SocialProvider})


@pytest.fixture()
def app(django_app_factory: "MixinWithInstanceVariables", admin_user: "User") -> DjangoTestApp:
    django_app: DjangoTestApp = django_app_factory(csrf_checks=False)
    django_app.set_user(admin_user)
    django_app._user = admin_user
    return django_app


def test_validate(app: DjangoTestApp, push_assignment: "Assignment") -> None:
    url = reverse("admin:webpush_browser_validate", args=[push_assignment.pk])
    app.get(url).follow()
    push_assignment.refresh_from_db()
    assert push_assignment.validated
