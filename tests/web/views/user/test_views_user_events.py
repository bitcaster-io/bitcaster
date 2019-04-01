import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


def test_user_event(django_app, event1, subscriber1):
    url = reverse('user-events', args=[event1.application.organization.slug])
    res = django_app.get(url, user=subscriber1)
    assert event1.name in str(res.body)
    res = res.click(href='subscribe')
    res.form['channels'] = [str(event1.channels.first().id)]
    res = res.form.submit('Save')
    # assert res.status_code == 200
