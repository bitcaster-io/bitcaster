import pytest


@pytest.mark.django_db
def test_subscription_list(django_app, application1):
    organization = application1.organization
    owner = organization.owner
    url = application1.urls.subscriptions
    res = django_app.get(url, user=owner.email)
    res.click('Invite People')
