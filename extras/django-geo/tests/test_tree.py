# -*- coding: utf-8 -*-
import pytest
from django.core.exceptions import ValidationError
from geo.models import AdministrativeArea


@pytest.mark.django_db
def test_type_cannot_contains_same_type(hierachy):
    """ a Type cannot contain the same type
    """
    italy, regione, provincia, comune = hierachy

    regione = italy.admins.get(name='Regione')
    lazio = italy.areas.create(name='Lazio', type=regione)
    with pytest.raises(ValidationError):
        AdministrativeArea.objects.create(name='Lombardia',
                                          parent=lazio,
                                          type=regione)


@pytest.mark.django_db
def test_type_cannot_contains_parent_type(hierachy):
    """ a Type cannot contain the parent type
    """
    italy, regione, provincia, comune = hierachy

    roma = italy.areas.create(name='Comune di Roma', type=comune)
    torino = italy.areas.create(name='Comune di Torino', type=comune)
    roma.parent = torino
    with pytest.raises(ValidationError):
        roma.save()


@pytest.mark.django_db
def test_type_cannot_contains_parent_type(hierachy):
    """ a Type cannot contain the parent type
    """
    italy, regione, provincia, comune = hierachy

    roma = italy.areas.create(name='Comune di Roma', type=comune)
    torino = italy.areas.create(name='Comune di Torino', type=comune)
    roma.parent = torino
    with pytest.raises(ValidationError):
        roma.save()


@pytest.mark.django_db
def test_contains(hierachy):
    italy, regione, provincia, comune = hierachy

    lazio = italy.areas.create(name='Lazio', type=regione)
    rm = italy.areas.create(name='Provincia di Roma', type=provincia, parent=lazio)
    roma = italy.areas.create(name='Comune di Roma', type=comune, parent=rm)
    ostia = roma.locations.create(name='Ostia')

    assert regione in italy
    assert provincia in regione
    assert comune in provincia

    assert roma in rm
    assert rm in lazio
    assert lazio in italy

    assert ostia in roma


@pytest.mark.django_db
def test_related_fields(italy):
    regione = italy.admins.create(name='Regione')
    assert regione.country == italy

    lazio = italy.areas.create(name='Lazio', type=regione)
    assert lazio.country == italy

    piemonte = regione.areas.create(name='Piemonte')
    assert piemonte.type == regione
    assert piemonte.country == italy
    assert piemonte in italy


    # italy, regione, provincia, comune = hierachy
    #
    # lazio = italy.areas.create(name='Lazio', type=regione)
    # rm = italy.areas.create(name='Provincia di Roma', type=provincia, parent=lazio)
    # roma = italy.areas.create(name='Comune di Roma', type=comune, parent=rm)
    # ostia = roma.locations.create(name='Ostia')
    #
    # assert regione in italy
    # assert provincia in regione
    # assert comune in provincia
    #
    # assert roma in rm
    # assert rm  in lazio
    # assert lazio in italy
    #
    # assert ostia in roma
    # assert ostia in rm
    # assert ostia in lazio
    # assert ostia in italy
