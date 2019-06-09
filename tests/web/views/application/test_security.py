import pytest

from bitcaster.security import APP_ROLES


@pytest.mark.django_db
def test_application_admin(django_app, application1, user1):
    application1.add_member(user1, APP_ROLES.ADMIN)
    url = application1.urls.edit
    res = django_app.get(url, user=user1.email)
    assert res
