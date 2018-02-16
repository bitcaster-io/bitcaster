from __future__ import absolute_import, unicode_literals

from django.conf.urls import url

from geo.views import (
    AdministrativeAreaTypeView, AdministrativeAreaView, CountryView, CurrencyView, LocationTypeView, LocationView,)

urlpatterns = [
    url(r'^lookups/country/$',
        CountryView.as_view(),
        name='geo-lookup-country'),

    url(r'^lookups/location/$',
        LocationView.as_view(),
        name='geo-lookup-location'),

    url(r'^lookups/currency/$',
        CurrencyView.as_view(),
        name='geo-lookup-currency'),

    url(r'^lookups/locationtype/$',
        LocationTypeView.as_view(),
        name='geo-lookup-locationtype'),

    url(r'^lookups/administrativearea/$',
        AdministrativeAreaView.as_view(),
        name='geo-lookup-administrativearea'),

    url(r'^lookups/administrativeareatype/$',
        AdministrativeAreaTypeView.as_view(),
        name='geo-lookup-administrativeareatype'),
]
