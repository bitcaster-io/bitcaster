import pytest

from django.test import RequestFactory

from bitcaster.models import LogEntry, User
from bitcaster.utils.django import admin_toggle_bool_action, get_cache_prefix, url_related


@pytest.mark.django_db
def test_get_cache_prefix():
    prefix = get_cache_prefix()
    assert prefix.startswith(":")
    assert prefix.endswith(":")


@pytest.mark.django_db
def test_url_related():
    url = url_related(User, op="changelist", id=1)
    assert "/admin/bitcaster/user/" in url
    assert "id=1" in url


@pytest.mark.django_db
def test_admin_toggle_bool_action(rf: RequestFactory):
    user = User.objects.create(username="testuser", is_active=True)
    request = rf.get("/")
    request.user = user

    queryset = User.objects.filter(pk=user.pk)
    admin_toggle_bool_action(request, queryset, "is_active")

    user.refresh_from_db()
    assert user.is_active is False

    assert LogEntry.objects.filter(user_id=user.pk).exists()
