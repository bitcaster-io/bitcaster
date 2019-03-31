import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


def test_user_application(django_app, organization1, user1):
    # UserAddressesView
    url = reverse('user-applications', args=[organization1.slug])
    res = django_app.get(url, user=user1)
    assert res
