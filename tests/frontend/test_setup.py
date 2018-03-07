import pytest
from constance import config

pytestmark = pytest.mark.django_db


@pytest.fixture()
def initialize():
    config.INITIALIZED = False
    yield
    config.INITIALIZED = True


def test_setup(django_app, initialize):
    "home is always accessible"
    config.INITIALIZED = False
    res = django_app.get('/').follow()
    res.form["email"] = "sax@saxix.org"
    res.form["password1"] = "password"
    res.form["password2"] = "password"
    res = res.form.submit().follow()
    # res = res.click("Login")
    # res.form["username"] = "sax@saxix.org"
    # res.form["password"] = "password"
    # res = res.form.submit()
    assert res.status_code == 302
