from typing import TYPE_CHECKING

import pytest

from django.urls import reverse

from bitcaster.constants import bitcaster
from bitcaster.models import DistributionList, User

if TYPE_CHECKING:
    from django_webtest import DjangoTestApp
    from django_webtest.pytest_plugin import MixinWithInstanceVariables


@pytest.fixture
def app(django_app_factory: "MixinWithInstanceVariables", admin_user: "User") -> "DjangoTestApp":
    django_app = django_app_factory(csrf_checks=False)
    django_app.set_user(admin_user)
    django_app._user = admin_user
    return django_app


def test_get_protected_list(app: "DjangoTestApp") -> None:
    from testutils.factories import DistributionListFactory

    dl = DistributionListFactory(name=DistributionList.ADMINS, project__organization__name=bitcaster.ORGANIZATION)
    url = reverse("admin:bitcaster_distributionlist_change", args=[dl.pk])
    res = app.get(url)
    frm = res.forms["distributionlist_form"]

    assert "name" not in frm.fields
    assert not res.pyquery("a.deletelink")
