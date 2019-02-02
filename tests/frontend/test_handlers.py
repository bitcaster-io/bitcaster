import pytest

from bitcaster.config import urls
from bitcaster.web.views import handler404, handler500

pytestmark = pytest.mark.django_db


def test_handler404(django_app, application1):
    organization = application1.organization
    owner = organization.owner
    url = '/404/'
    res = django_app.get(url, user=owner.email, expect_errors=True)
    assert res.status_code == 404


def test_404(rf):
    assert urls.handler404.endswith('.handler404')
    request = rf.get('/')
    response = handler404(request)
    assert response.status_code == 404


def test_500(rf):
    assert urls.handler500.endswith('.handler500')
    request = rf.get('/')
    response = handler500(request)
    assert response.status_code == 500
