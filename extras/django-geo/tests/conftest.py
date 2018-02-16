import itertools
import os
import sys
from functools import partial

import factory
import pytest


from geo.models import AdministrativeArea, AdministrativeAreaType, Country, Currency, Location, LocationType, CONTINENTS


def pytest_collection_modifyitems(items):
    pass


def pytest_configure(config):
    here = os.path.dirname(__file__)
    sys.path.insert(0, os.path.join(here, 'demo'))


#####

class CurrencyFactory(factory.DjangoModelFactory):
    class Meta:
        model = Currency
        django_get_or_create = ('iso_code',)

    iso_code = factory.Faker("currency_code")
    numeric_code = factory.Sequence(lambda n: '{:05}'.format(n))


C = [a for (a, b) in CONTINENTS]


class CountryFactory(factory.DjangoModelFactory):
    class Meta:
        model = Country
        django_get_or_create = ('iso_code',)

    iso_code = factory.Faker('country_code')
    iso_code3 = factory.Sequence(lambda n: '{:03}'.format(n))
    iso_num = factory.Sequence(lambda n: '{:03}'.format(n))
    name = factory.Sequence(lambda n: 'Country{:03}'.format(n))
    currency = factory.SubFactory(CurrencyFactory)
    continent = factory.Iterator(C)
    # email = factory.LazyAttribute(lambda a: '{0}.{1}@example.com'.format(a.first_name, a.last_name).lower())
    # email = factory.Sequence(lambda n: 'person{0}@example.com'.format(n))
    # language = factory.Iterator(models.Language.objects.all())
    # log = factory.RelatedFactory(UserLogFactory, 'user', action=models.UserLog.ACTION_CREATE)


class AdministrativeAreaTypeFactory(factory.DjangoModelFactory):
    class Meta:
        model = AdministrativeAreaType

    country = factory.SubFactory(CountryFactory)
    name = factory.Sequence(lambda n: 'AreaType{:03}'.format(n))


class AdministrativeAreaFactory(factory.DjangoModelFactory):
    class Meta:
        model = AdministrativeArea

    type = factory.SubFactory(AdministrativeAreaTypeFactory)
    name = factory.Sequence(lambda n: 'Area{:03}'.format(n))

    parent = None

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        kwargs['country'] = kwargs['type'].country
        return super(AdministrativeAreaFactory, cls)._create(model_class, *args, **kwargs)


class LocationTypeFactory(factory.DjangoModelFactory):
    class Meta:
        model = LocationType


class LocationFactory(factory.DjangoModelFactory):
    class Meta:
        model = Location

    area = factory.SubFactory(AdministrativeAreaFactory)
    type = factory.SubFactory(LocationTypeFactory)

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        kwargs['country'] = kwargs['area'].country
        return super(LocationFactory, cls)._create(model_class, *args, **kwargs)


name = lambda prefix, sequence: "{0}-{1}".format(prefix, next(sequence))
nextname = partial(name, sequence=itertools.count())

counter = itertools.count()


@pytest.fixture
def hierachy():
    italy = CountryFactory(iso_code='IT')
    regione = AdministrativeAreaTypeFactory(name='Regione', country=italy)
    provincia = AdministrativeAreaTypeFactory(name='Provincia', parent=regione)
    comune = AdministrativeAreaTypeFactory(name='Comune', parent=provincia)

    # lazio = AdministrativeAreaTypeFactory(name='Lazio', type=regione)
    # roma = AdministrativeAreaTypeFactory(name='Roma', type=provincia, parent=lazio)
    # ciampino = AdministrativeAreaTypeFactory(name='Comune', type=comune, parent=roma)

    return italy, regione, provincia, comune


# def subargs(kwargs, prefix):
#     prefix = "%s__" % prefix
#     ret = {key[len(prefix):]: kwargs.pop(key) for key in kwargs.keys() if key.startswith(prefix)}
#     return ret


@pytest.fixture
def currency():
    return CurrencyFactory()


@pytest.fixture
def country():
    return CountryFactory()


@pytest.fixture
def italy():
    return CountryFactory(iso_code='IT', iso_code3='ITA', name="Italy",
                          continent='EU')


@pytest.fixture
def usa():
    return CountryFactory(iso_code='US', iso_code3='USA',
                          name="United States Of America",
                          continent='NA')

@pytest.fixture
def uk():
    return CountryFactory(iso_code='GB', iso_code3='GBR',
                          name="United Kingdom",
                          continent='EU')


@pytest.fixture
def area():
    return AdministrativeAreaFactory()


@pytest.fixture
def location():
    return LocationFactory()

#
# def country_factory(**kwargs):
#     country_name = partial(name, sequence=itertools.count(start=0))
#
#     kwargs.setdefault('iso_code', lambda x: "{:02}".format(next(counter))[:2])
#     kwargs.setdefault('iso_code3', lambda x: "{:03}".format(next(counter))[:3])
#     kwargs.setdefault('undp', lambda x: "{:03}".format(next(counter))[:3])
#     kwargs.setdefault('nato3', lambda x: "{:03}".format(next(counter))[:3])
#     kwargs.setdefault('iso_num', lambda x: "{:03}".format(next(counter))[:3])
#
#     kwargs.setdefault('name', lambda x: country_name('Country'))
#     kwargs.setdefault('currency', None)
#
#     country = G(Country, **kwargs)
#     return country
#
#
# def area_tree_factory(country):
#     parent = area_factory(country, name=nextname('RegionArea'), type__name=nextname('Region'))
#     area = area_factory(parent=parent, name=nextname('SubRegionArea'), type__name=nextname('SubRegion'))
#     location = location_factory(area=area)
#     return parent, area, location
#
#
# def area_type_factory(country, **kwargs):
#     kwargs.setdefault('name', nextname('AdministrativeAreaType'))
#     kwargs.setdefault('parent', None)
#     return AdministrativeAreaType.objects.get_or_create(country=country, **kwargs)[0]
#
#
# def area_factory(country=None, **kwargs):
#     if 'parent' in kwargs:
#         country = kwargs['parent'].country
#         type_kwargs = subargs(kwargs, 'type')
#         type_kwargs['country'] = country
#         type_kwargs['parent'] = kwargs['parent'].type
#         kwargs['type'] = area_type_factory(**type_kwargs)
#     else:
#         type_kwargs = subargs(kwargs, 'type')
#         type_kwargs['country'] = country
#         kwargs['type'] = area_type_factory(**type_kwargs)
#
#     kwargs.setdefault('parent', None)
#     kwargs.setdefault('name', nextname('AdministrativeArea'))
#
#     return AdministrativeArea.objects.get_or_create(country=country, **kwargs)[0]
#
#
# def location_type_factory(**kwargs):
#     return G(LocationType, **kwargs)
#
#
# def location_factory(**kwargs):
#     if 'area' in kwargs:
#         kwargs['country'] = kwargs['area'].country
#     else:
#         if not 'country' in kwargs:
#             kwargs['country'] = country_factory(**subargs(kwargs, 'country'))
#         area_kwargs = subargs(kwargs, 'area')
#         area_kwargs['country'] = kwargs['country']
#         kwargs['area'] = area_factory(**area_kwargs)
#     if 'type' not in kwargs:
#         kwargs['type'] = location_type_factory(**subargs(kwargs, 'type'))
#
#     kwargs.setdefault('name', nextname('Location'))
#     location = G(Location, **kwargs)
#     return location
