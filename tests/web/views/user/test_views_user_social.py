import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


def test_social_login(django_app, organization1):
    # UserSocialAuthView
    url = reverse('user-socialauth', args=[organization1.slug])
    res = django_app.get(url, user=organization1.owner)
    assert res


def test_social_logout(django_app, organization1):
    # UserSocialAuthDisconnectView
    url = reverse('user-socialauth-disconnect', args=[organization1.slug, 'github-org'])
    res = django_app.get(url, user=organization1.owner)
    assert res
