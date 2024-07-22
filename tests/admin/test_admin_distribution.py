from typing import TYPE_CHECKING

import pytest
from django.urls import reverse
from testutils.factories import DistributionListFactory

if TYPE_CHECKING:
    from django_webtest import DjangoTestApp
    from django_webtest.pytest_plugin import MixinWithInstanceVariables

    from bitcaster.models import User


@pytest.fixture()
def app(django_app_factory: "MixinWithInstanceVariables", admin_user: "User") -> "DjangoTestApp":
    django_app = django_app_factory(csrf_checks=False)
    django_app.set_user(admin_user)
    django_app._user = admin_user
    return django_app


def test_get_protected_list(app: "DjangoTestApp") -> None:
    from bitcaster.models import DistributionList

    dl = DistributionListFactory(name=DistributionList.ADMINS)
    url = reverse("admin:bitcaster_distributionlist_change", args=[dl.pk])
    res = app.get(url)
    frm = res.forms["distributionlist_form"]

    assert "name" not in frm.fields
    assert not res.pyquery("a.deletelink")
