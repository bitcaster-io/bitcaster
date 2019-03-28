import pytest
import pytz
from django.urls import reverse

pytestmark = pytest.mark.django_db


def test_user_profile(django_app, organization1, admin):
    # UserProfileView
    url = reverse('user-profile', args=[organization1.slug])
    res = django_app.get(url, user=admin)
    res.form['friendly_name'] = 'Name'
    res.form['timezone'].force_value(pytz.timezone('Europe/Rome'))
    res.form['country'].force_value('IT')
    res = res.form.submit()
    assert res.status_code == 302, f"Submit failed with: {repr(res.context['form'].errors)}"
