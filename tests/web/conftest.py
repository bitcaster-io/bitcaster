from typing import TYPE_CHECKING

import pytest
from django.http import HttpRequest
from django.test.client import RequestFactory
from django_webtest import DjangoTestApp
from django_webtest.pytest_plugin import MixinWithInstanceVariables

from bitcaster.models import User
from bitcaster.state import state

if TYPE_CHECKING:
    from pytest_django.fixtures import SettingsWrapper


@pytest.fixture()
def app(
    django_app_factory: "MixinWithInstanceVariables",
    rf: "RequestFactory",
    admin_user: "User",
    settings: "SettingsWrapper",
) -> "DjangoTestApp":
    settings.FLAGS = {"BETA_PREVIEW_LOCKING": [("boolean", True)]}

    django_app = django_app_factory(csrf_checks=False)
    django_app.set_user(admin_user)
    django_app._user = admin_user
    request: HttpRequest = rf.get("/")
    request.user = admin_user
    with state.configure(request=request):
        yield django_app
