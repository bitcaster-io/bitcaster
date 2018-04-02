# -*- coding: utf-8 -*-
import pytest

from bitcaster.models import Application


@pytest.mark.django_db
def test_save_application_with_slug(organization1):
    a = Application(organization=organization1,
                    name='app1', slug='app1')
    a.save()
    assert a.pk


@pytest.mark.django_db
def test_save_application_without_slug(organization1):
    a = Application(organization=organization1, name='app1')
    a.save()
    assert a.pk
