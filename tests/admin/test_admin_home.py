from typing import TYPE_CHECKING

import uuid

from flags.state import disable_flag

import pytest
from unittest.mock import patch

from django.db.models import Count
from django.urls import reverse

if TYPE_CHECKING:
    from django_webtest import DjangoTestApp
    from django_webtest.pytest_plugin import MixinWithInstanceVariables

    from bitcaster.models import User


@pytest.fixture
def app(django_app_factory: "MixinWithInstanceVariables", admin_user: "User") -> "DjangoTestApp":
    django_app = django_app_factory(csrf_checks=False)
    django_app.set_user(admin_user)
    django_app._user = admin_user
    return django_app


def test_home_dashboard(app: "DjangoTestApp", occurrence, settings) -> None:
    url = reverse("admin:index")
    settings.CACHE_PREFIX = uuid.uuid4().hex
    disable_flag("DISABLE_CACHE")
    from bitcaster.models import Occurrence

    qs = Occurrence.objects.values("status").annotate(count=Count("id"))
    with patch("bitcaster.models.Occurrence.objects.filter") as mock_filter:
        mock_filter.return_value = qs
        # First call: should query the database (filter called) and populate cache
        res = app.get(url)
        assert res.status_code == 200
        call_count_after_first = mock_filter.call_count
        assert call_count_after_first > 0

    with patch("bitcaster.models.Occurrence.objects.filter") as mock_filter:
        # Second call: should hit the cache, so filter should NOT be called again
        res2 = app.get(url)
        assert res2.status_code == 200
        assert mock_filter.call_count < call_count_after_first
