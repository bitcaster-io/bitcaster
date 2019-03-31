import pytest
from django.urls import reverse

from bitcaster.models import Subscription

pytestmark = pytest.mark.django_db


def test_user_subscriptions(django_app, subscription1):
    url = reverse('user-subscriptions', args=[subscription1.event.application.organization.slug])
    res = django_app.get(url, user=subscription1.subscriber)
    assert subscription1.event.name in str(res.body)


def test_user_subscriptions_toggle(django_app, subscription1):
    url = reverse('user-subscriptions', args=[subscription1.event.application.organization.slug])
    res = django_app.get(url, user=subscription1.subscriber)
    res = res.click(href='toggle/').follow()

    subscription1.refresh_from_db()
    assert not subscription1.enabled

    res = res.click(href='toggle/').follow()
    subscription1.refresh_from_db()
    assert subscription1.enabled


def test_user_subscriptions_remove(django_app, subscription1):
    url = reverse('user-subscriptions', args=[subscription1.event.application.organization.slug])
    res = django_app.get(url, user=subscription1.subscriber)
    res = res.click(href='delete/')
    res = res.form.submit()
    assert not Subscription.objects.filter(pk=subscription1.id).exists()


def test_user_subscriptions_edit(django_app, subscription1):
    url = reverse('user-subscriptions', args=[subscription1.event.application.organization.slug])
    res = django_app.get(url, user=subscription1.subscriber)
    res = res.click(href='edit/')
    res = res.form.submit()
    assert res.status_code == 302
