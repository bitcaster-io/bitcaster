import django_webtest
import pytest
from django.core.urlresolvers import reverse

from geo.models import AdministrativeArea, AdministrativeAreaType, Country


#
# @pytest.fixture(scope='function')
# def app(request):
#     wtm = django_webtest.WebTestMixin()
#     wtm._patch_settings()
#     wtm._setup_auth()
#     request.addfinalizer(wtm._unpatch_settings)
#     wtm.renew_app()
#     return wtm.app
#     # return django_webtest.DjangoTestApp()
#

@pytest.mark.django_db
def test_country_update(django_app, admin_user, country):
    url = reverse('admin:geo_country_changelist')
    res = django_app.get(url, user=admin_user.username)
    res = res.click("^{}$".format(country.name))
    res = res.form.submit()

    assert res.status_code == 200


@pytest.mark.django_db
def test_areatype_update(django_app, hierachy, admin_user):
    italy, regione, provincia, comune = hierachy
    url = reverse('admin:geo_administrativeareatype_changelist')

    res = django_app.get(url, user=admin_user.username)
    res = res.click("^{}$".format(regione.name))
    res = res.form.submit().follow()


@pytest.mark.django_db
def test_area_update(django_app, hierachy, admin_user, area):
    italy, regione, provincia, comune = hierachy
    url = reverse('admin:geo_administrativearea_changelist')

    res = django_app.get(url, user=admin_user.username)
    res = res.click("^{}$".format(area.name))
    res = res.form.submit().follow()



@pytest.mark.django_db
def test_currency(django_app, admin_user, currency):
    url = reverse('admin:geo_currency_changelist')
    res = django_app.get(url, user=admin_user.username)
    assert res.status_code == 200
