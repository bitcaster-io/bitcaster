from typing import TYPE_CHECKING

import pytest
from django.urls import reverse
from testutils.factories import AssignmentFactory

from bitcaster.models import Assignment, DistributionList, User

if TYPE_CHECKING:
    from django_webtest import DjangoTestApp
    from django_webtest.pytest_plugin import MixinWithInstanceVariables


@pytest.fixture()
def app(django_app_factory: "MixinWithInstanceVariables", admin_user: "User") -> "DjangoTestApp":
    django_app = django_app_factory(csrf_checks=False)
    django_app.set_user(admin_user)
    django_app._user = admin_user
    return django_app


def test_add_to_distributionlist(app: "DjangoTestApp", distributionlist: "DistributionList") -> None:
    AssignmentFactory.create_batch(5)
    url = reverse("admin:bitcaster_user_changelist")
    res = app.get(url)
    frm = res.forms["changelist-form"]
    selected_users = []
    for i in range(len(res.pyquery("input[name=_selected_action]"))):
        frm.get("_selected_action", index=i).checked = True
        selected_users.append(frm.get("_selected_action", index=i).value)
    frm["action"] = "add_to_distributionlist"
    res = frm.submit()
    frm = res.forms["action-form"]
    res = frm.submit("apply")
    assert res.status_code == 200

    frm = res.forms["action-form"]
    frm["dl"] = distributionlist.pk
    res = frm.submit("apply")
    assert res.status_code == 302, res.context["form"].errors
    assert distributionlist.recipients.count() == Assignment.objects.filter(address__user__in=selected_users).count()
