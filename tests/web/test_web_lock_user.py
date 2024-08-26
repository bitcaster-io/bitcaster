from typing import TYPE_CHECKING, TypedDict

import pytest
from django.urls import reverse
from django_webtest import DjangoTestApp
from django_webtest.pytest_plugin import MixinWithInstanceVariables

from bitcaster.forms.locking import LockingModeChoice
from bitcaster.models import User

if TYPE_CHECKING:

    Context = TypedDict(
        "Context",
        {
            "user": User,
            "locked_user": User,
            "admin_user": User,
        },
    )


@pytest.fixture
def context(django_app_factory: "MixinWithInstanceVariables", admin_user: "User") -> "Context":
    from testutils.factories import UserFactory

    user = UserFactory()
    locked_user = UserFactory(locked=True)

    return {"user": user, "locked_user": locked_user, "admin_user": admin_user}


def test_byuser(app: DjangoTestApp, context: "Context") -> None:
    from bitcaster.models import User

    url = reverse("locking")
    res = app.get(url)
    assert res.status_code == 200

    users = set(User.objects.filter(locked=True).values_list("id", flat=True))
    assert users == {context["locked_user"].id}

    res.form["mode-operation"] = LockingModeChoice.USER
    res = res.form.submit()

    assert sorted(res.form.fields["user-user"][0].options) == sorted(
        [
            ("", True, "All"),
            (str(context["user"].id), False, context["user"].username),
            (str(context["admin_user"].id), False, context["admin_user"].username),
        ]
    )
    res.form.fields["user-user"][0].select(str(context["user"].id))
    res = res.form.submit()
    assert res.status_code == 200

    users = set(User.objects.filter(locked=True).values_list("id", flat=True))
    assert users == {context["locked_user"].id, context["user"].id}

    assert "The following users have been locked" in res.text
    assert context["locked_user"].username not in res.text
    assert context["user"].username in res.text
