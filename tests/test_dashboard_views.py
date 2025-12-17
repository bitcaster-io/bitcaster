from unittest.mock import patch

import pytest
from django.urls import reverse
from testutils.perms import user_grant_permissions

from bitcaster.models import User

pytestmark = pytest.mark.django_db


def test_tools_view_get(django_app, user: User):
    url = reverse("admin:console-toolsview")
    res = django_app.get(url, user=user, expect_errors=True)
    assert res.status_code == 403
    with user_grant_permissions(user, ["bitcaster.console_tools"]):
        res = django_app.get(url, user=user)
    assert res.status_code == 200


@patch("bitcaster.web.dashboard.views.CacheManager")
def test_tools_view_post_clear_cache(mock_cache_manager, django_app, user):
    url = reverse("admin:console-toolsview")
    with user_grant_permissions(user, ["bitcaster.console_tools"]):
        res = django_app.get(url, user=user)
        res = res.forms["clear_cache"].submit("op")
    assert res.status_code == 200
    mock_cache_manager.return_value.clear_cache.assert_called_once()


def test_lock_view_get(django_app, user):
    url = reverse("admin:console-lockview")
    with user_grant_permissions(user, ["bitcaster.console_lock"]):
        res = django_app.get(url, user=user)
    assert res.status_code == 200


@patch("bitcaster.models.Application.lock")
def test_lock_view_post_lock_application(mock_lock, django_app, user, application):
    url = reverse("admin:console-lockview")
    with user_grant_permissions(user, ["bitcaster.console_lock"]):
        res = django_app.get(url, user=user)
        res.forms["lock-application"]["target"] = application.id
        res.forms["lock-application"].submit()
    mock_lock.assert_called_once()


@patch("bitcaster.models.Application.pause")
def test_lock_view_post_pause_event(mock_pause, django_app, user, application):
    url = reverse("admin:console-lockview")
    with user_grant_permissions(user, ["bitcaster.console_lock"]):
        res = django_app.get(url, user=user)
        res.forms["pause-application"]["target"] = application.id
        res.forms["pause-application"].submit()
    mock_pause.assert_called_once()
