import pytest
from constance import config
from constance.test import override_config

from bitcaster.models import User

pytestmark = pytest.mark.django_db


@pytest.fixture()
def initialize():
    config.INITIALIZED = False
    yield
    config.INITIALIZED = True


def test_setup(django_app, initialize):
    email = 'sax@saxix.org'
    res = django_app.get('/').follow()
    res.form['organization'] = 'Organization1'
    res.form['email'] = email
    res.form['password1'] = 'password'
    res = res.form.submit()
    assert res.status_code == 200

    res.form['password1'] = 'password'
    res.form['password2'] = 'pwd'
    res = res.form.submit()
    assert res.status_code == 200

    res.form['password1'] = 'password'
    res.form['password2'] = 'password'
    res = res.form.submit()
    assert res.status_code == 302, f"Submit failed with: {repr(res.context['form'].errors)}"

    user = User.objects.filter(email=email).first()
    assert user

    org = user.memberships.first().organization
    assert org.memberships.filter(user=user).exists()


@override_config(INITIALIZED=True)
def test_setup_initialized(django_app, initialize):
    res = django_app.get('/setup/', expect_errors=True)
    assert res.status_code == 404
