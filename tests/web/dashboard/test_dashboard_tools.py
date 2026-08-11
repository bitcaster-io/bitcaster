from webtest import TestApp

import pytest
from testutils.helpers import assert_message
from testutils.perms import user_grant_permissions

from django.urls import reverse

pytestmark = pytest.mark.django_db


def test_tools_view_get(django_app, user):
    url = reverse("admin:console-toolsview")
    with user_grant_permissions(user, ["bitcaster.console_tools"]):
        res = django_app.get(url, user=user)
    assert res.status_code == 200


def test_tools_view_post(django_app: TestApp, user, application):
    url = reverse("admin:console-toolsview")
    with user_grant_permissions(user, ["bitcaster.console_tools"]):
        res = django_app.get(url, user=user)
        res = res.forms["clear_cache"].submit("op").follow()
        assert_message(res, "Cache cleared")
    with user_grant_permissions(user, ["bitcaster.console_tools"]):
        res = django_app.get(url, user=user)
        res = res.forms["clear_cache"].submit().follow()
        assert_message(res, "Nothing selected")
