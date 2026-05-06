import pytest
from testutils.perms import user_grant_permissions
from unittest import mock

from django.urls import reverse

pytestmark = pytest.mark.django_db


def test_monitor_view_get(django_app, user):
    url = reverse("admin:console-monitorview")

    with user_grant_permissions(user, ["bitcaster.console_tools"]):
        res = django_app.get(url, user=user)
    assert res.status_code == 200
    assert "monitor.min.js" in res.text


def test_monitor_view_post(django_app_factory, user):
    django_app = django_app_factory(csrf_checks=False)
    url = reverse("admin:console-monitorview")
    with mock.patch("bitcaster.runner.manager.BackgroundManager") as mockbackgroundmanager:
        mock_manager = mockbackgroundmanager.return_value
        mock_manager.get_runners.return_value = ["worker1"]
        mock_manager.scheduler_info.return_value = {"status": True}

        with user_grant_permissions(user, ["bitcaster.console_tools"]):
            res = django_app.post(url, user=user)
    assert res.status_code == 200
    data = res.json
    assert data["beat"]["status"] is True
    assert "worker1" in data["workers"]
