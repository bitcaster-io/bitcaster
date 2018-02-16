# -*- coding: utf-8 -*-

from django.utils.translation import gettext as _
from geo.models import Country


def adm_italy():
    italy = Country.objects.get(iso_code='IT')
    regione, __ = italy.admins.get_or_create(name='Regione')
    provincia, __ = italy.admins.get_or_create(name='Provincia',
                                               parent=regione)
    comune, __ = italy.admins.get_or_create(name='Comune',
                                            parent=provincia)
    return italy, regione, provincia, comune


def adm_usa():
    usa = Country.objects.get(iso_code='US')
    state, __ = usa.admins.get_or_create(name='State')
    county, __ = usa.admins.get_or_create(name='County',
                                          parent=state)
    township, __ = usa.admins.get_or_create(name='Township',
                                            parent=county)
    return usa, state, county, township


def adm_uk():
    uk = Country.objects.get(iso_code='GB')
    state, __ = uk.admins.get_or_create(name='Region')
    county, __ = state.children.get_or_create(name='County')
    township, __ = county.children.get_or_create(name='Township')
    parish, __ = township.children.get_or_create(name='Parish')

    return uk, state, county, township, parish
