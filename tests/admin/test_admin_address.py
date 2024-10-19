from typing import Any

import pytest
from django.urls import reverse
from django_webtest import DjangoTestApp
from django_webtest.pytest_plugin import MixinWithInstanceVariables

from bitcaster.constants import AddressType


@pytest.fixture()
def app(django_app_factory: MixinWithInstanceVariables, db: Any) -> DjangoTestApp:
    from testutils.factories import SuperUserFactory

    django_app = django_app_factory(csrf_checks=False)
    admin_user = SuperUserFactory(username="superuser")
    django_app.set_user(admin_user)
    django_app._user = admin_user
    return django_app


def test_add_and_redirect(app: DjangoTestApp) -> None:
    base_url = reverse("admin:bitcaster_address_add")
    url = f"{base_url}?next=www.bitcaster.io"
    res = app.post(url, {"user": -1})
    assert res.status_code == 200
    res = app.post(
        url,
        {"user": app._user.pk, "name": "address #1", "type": AddressType.EMAIL, "value": "me@bitcaster.io"},
    )
    assert res.status_code == 302
    assert res.location == "www.bitcaster.io"


@pytest.mark.parametrize(
    "value, t",
    [("user@email.com", AddressType.EMAIL), ("+12299088128", AddressType.PHONE), ("account", AddressType.ACCOUNT)],
)
def test_add_address_types(app: DjangoTestApp, value: str, t: AddressType) -> None:
    base_url = reverse("admin:bitcaster_address_add")
    url = f"{base_url}?next=www.bitcaster.io"
    res = app.post(url, {"user": app._user.pk, "name": "address #1", "value": value, "type": AddressType.GENERIC})
    assert res.status_code == 302
    assert res.location == "www.bitcaster.io"
