import pytest

from bitcaster.models import Application


@pytest.mark.django_db
def test_application_delete(django_app, application1):
    url = application1.urls.delete

    res = django_app.get(url, user=application1.organization.owner)
    res = res.form.submit()
    assert not Application.objects.filter(id=application1.id).exists()
