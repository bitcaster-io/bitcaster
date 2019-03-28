import pytest
from constance.test import override_config
from django.urls import reverse

pytestmark = pytest.mark.django_db


@override_config(SYSTEM_CONFIGURED=0)
def test_owner_index_not_configured(django_app, organization1):
    # UserIndexView
    url = reverse('me', args=[organization1.slug])
    res = django_app.get(url, user=organization1.owner)
    assert res.status_code == 200


@override_config(SYSTEM_CONFIGURED=0)
def test_admin_index_not_configured(django_app, organization1, admin):
    # UserIndexView
    url = reverse('me', args=[organization1.slug])
    res = django_app.get(url, user=admin)
    assert res.status_code == 200


def test_user_index(django_app, subscription1, monkeypatch):
    # UserIndexView
    app = subscription1.channel.application
    org = app.organization
    url = reverse('me', args=[org.slug])
    res = django_app.get(url, user=org.owner)
    assert res.status_code == 200
