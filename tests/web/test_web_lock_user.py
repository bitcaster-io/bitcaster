from typing import TYPE_CHECKING, TypedDict

import pytest
from django.urls import reverse
from django_webtest import DjangoTestApp

from bitcaster.forms.locking import LockingModeChoice
from bitcaster.models import User
from bitcaster.state import state

if TYPE_CHECKING:

    Context = TypedDict(
        "Context",
        {
            "user": User,
            "locked_user": User,
            "admin_user": User,
        },
    )


@pytest.fixture()
def app(django_app_factory, rf, db, admin_user):
    django_app = django_app_factory(csrf_checks=False)
    django_app.set_user(admin_user)
    django_app._user = admin_user
    request = rf.get("/")
    request.user = admin_user
    with state.configure(request=request):
        yield django_app


@pytest.fixture
def context(django_app_factory, admin_user) -> "Context":
    from testutils.factories.org import UserFactory

    user = UserFactory()
    locked_user = UserFactory(locked=True)

    return {"user": user, "locked_user": locked_user, "adminuser": admin_user}


def test_byuser(app: DjangoTestApp, context):
    from bitcaster.models import User

    url = reverse("locking")
    res = app.get(url)
    assert res.status_code == 200

    users = set(User.objects.filter(locked=True).values_list("id", flat=True))
    assert users == {context["locked_user"].id}

    res.form["mode-operation"] = LockingModeChoice.USER
    res = res.form.submit()

    assert res.form.fields["user-user"][0].options == [
        ("", True, "All"),
        (str(context["user"].id), False, context["user"].username),
        (str(context["adminuser"].id), False, context["adminuser"].username),
    ]

    res.form.fields["user-user"][0].select(str(context["user"].id))
    res = res.form.submit()
    assert res.status_code == 200

    users = set(User.objects.filter(locked=True).values_list("id", flat=True))
    assert users == {context["locked_user"].id, context["user"].id}

    assert "The following users have been locked" in res.text
    assert context["locked_user"].username not in res.text
    assert context["user"].username in res.text
