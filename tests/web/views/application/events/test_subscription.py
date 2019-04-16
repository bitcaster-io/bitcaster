import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


def test_event_subscriptions_list(django_app, subscription1, user1):
    event = subscription1.event
    application = event.application
    organization = application.organization
    url = reverse('app-event-subscriptions', args=[organization.slug,
                                                   application.slug,
                                                   event.pk])
    res = django_app.get(url, user=user1)
    assert b'User subscribed to event' in res.body


def test_event_subscriptions_toggle(django_app, subscription1, user1):
    event = subscription1.event
    application = event.application
    organization = application.organization
    url = reverse('app-event-subscription-toggle', args=[organization.slug,
                                                         application.slug,
                                                         event.pk,
                                                         subscription1.pk])
    django_app.get(url, user=user1)
    subscription1.refresh_from_db()
    assert not subscription1.enabled


def test_subscription_delete(django_app, subscription1, user1):
    event = subscription1.event
    application = event.application
    organization = application.organization
    url = reverse('app-event-subscription-delete', args=[organization.slug,
                                                         application.slug,
                                                         event.pk,
                                                         subscription1.pk])
    res = django_app.get(url, user=user1)
    res = res.form.submit()
    assert res.status_code == 302, f"Submit failed with: {repr(res.context['form'].errors)}"
    assert not event.subscriptions.filter(pk=subscription1.pk).exists()
