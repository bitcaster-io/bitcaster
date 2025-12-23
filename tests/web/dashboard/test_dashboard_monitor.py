from unittest.mock import patch

import pytest
from django.urls import reverse
from django.utils import timezone
from testutils.perms import user_grant_permissions

pytestmark = pytest.mark.django_db


def test_monitor_view_get(django_app, user):
    url = reverse("admin:console-monitorview")

    with user_grant_permissions(user, ["bitcaster.console_tools"]):
        res = django_app.get(url, user=user)
    assert res.status_code == 200
    assert "monitor.min.js" in res.text


@patch("bitcaster.web.dashboard.views.list_running_tasks", return_value={"worker1": []})
@patch("bitcaster.web.dashboard.views.last_seen_beat")
@patch("bitcaster.web.dashboard.views.is_worker_running", return_value=True)
def test_monitor_view_post(
    mock_is_worker_running, mock_last_seen_beat, mock_list_running_tasks, django_app_factory, user
):
    django_app = django_app_factory(csrf_checks=False)
    mock_last_seen_beat.return_value = {"status": True, "seen": timezone.now().isoformat()}
    url = reverse("admin:console-monitorview")
    with user_grant_permissions(user, ["bitcaster.console_tools"]):
        res = django_app.post(url, user=user)
    assert res.status_code == 200
    data = res.json
    assert data["alive"] is True
    assert data["beat"]["status"] is True
    assert "worker1" in data["workers"]
