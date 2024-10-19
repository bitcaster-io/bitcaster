# mypy: disable-error-code="union-attr"
from typing import TYPE_CHECKING

import pytest
from django.http import HttpRequest
from django.test.client import RequestFactory
from django.urls import reverse
from django_webtest import DjangoTestApp
from django_webtest.pytest_plugin import MixinWithInstanceVariables
from pytest_factoryboy import register
from testutils.factories import (
    ChannelFactory,
    OrganizationFactory,
    ProjectFactory,
    UserFactory,
)

from bitcaster.state import state

if TYPE_CHECKING:

    from bitcaster.models import Channel, Group

register(UserFactory)
register(OrganizationFactory)
register(ChannelFactory, "channel")
register(ProjectFactory, "project")


@pytest.fixture()
def app(django_app_factory: MixinWithInstanceVariables, rf: RequestFactory) -> DjangoTestApp:
    from testutils.factories import SuperUserFactory

    django_app = django_app_factory(csrf_checks=False)
    admin_user = SuperUserFactory(username="superuser")
    django_app.set_user(admin_user)
    django_app._user = admin_user
    request: HttpRequest = rf.get("/")
    request.user = admin_user

    with state.configure(request=request):
        yield django_app


def test_save_constance(app: DjangoTestApp, group: "Group", email_channel: "Channel") -> None:
    url = reverse("admin:constance_config_changelist")
    res = app.get(url)
    res = res.forms["changelist-form"].submit()
    assert res.status_code == 302
