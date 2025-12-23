import pytest
from django.urls import reverse
from testutils.perms import user_grant_permissions

pytestmark = pytest.mark.django_db


def test_lock_view_get(django_app, user):
    url = reverse("admin:console-lockview")
    with user_grant_permissions(user, ["bitcaster.console_lock"]):
        res = django_app.get(url, user=user)
    assert res.status_code == 200


def test_lock_view_post_lock_application(django_app, user, application):
    url = reverse("admin:console-lockview")
    with user_grant_permissions(user, ["bitcaster.console_lock"]):
        res = django_app.get(url, user=user)
        res.forms["lock-application"]["target"] = application.id
        res.forms["lock-application"].submit()
    application.refresh_from_db()
    assert application.locked


def test_lock_view_post_pause_event(django_app, user, application):
    url = reverse("admin:console-lockview")
    with user_grant_permissions(user, ["bitcaster.console_lock"]):
        res = django_app.get(url, user=user)
        res.forms["pause-application"]["target"] = application.id
        res.forms["pause-application"].submit()
    application.refresh_from_db()
    assert application.paused
