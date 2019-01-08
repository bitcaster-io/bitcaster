import pytest
from constance import config

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
    res.form['email'] = email
    res.form['password1'] = 'password'
    res.form['password2'] = 'password'
    res = res.form.submit().follow()
    assert res.status_code == 302

    user = User.objects.filter(email=email).first()
    assert user

    org = user.memberships.first().organization
    assert org.memberships.filter(user=user).exists()
