import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


def test_event_list(django_app, event1, user1):
    application = event1.application
    organization = application.organization
    url = reverse('app-events', args=[organization.slug,
                                      application.slug])
    res = django_app.get(url, user=user1)
    assert event1.name in str(res.body)
