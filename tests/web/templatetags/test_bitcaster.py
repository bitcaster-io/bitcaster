from unittest.mock import MagicMock

import pytest
from django.forms import inlineformset_factory
from django.template import Library
from rest_framework.fields import Field
from rest_framework.serializers import Serializer

from bitcaster.models import Application, Organization, User
from bitcaster.web.templatetags.bitcaster import (app_reverse,
                                                  channel_submit_row, httpiefy,
                                                  jsonify, order_formset,
                                                  org_reverse, render_field,
                                                  render_serializer,
                                                  verbose_name,
                                                  verbose_name_plural,)

register = Library()


@pytest.mark.parametrize('value', ['', {'a': 1}])
def test_httpiefy(value):
    httpiefy(value)


@pytest.mark.parametrize('value', ['', {'a': 1}])
def test_jsonify(value):
    jsonify(value)


def test_verbose_name():
    assert verbose_name(User())


# @register.filter()
def test_verbose_name_plural():
    assert verbose_name_plural(User())


def test_channel_submit_row():
    assert channel_submit_row(MagicMock())


@pytest.mark.django_db
def test_app_reverse(application1):
    assert app_reverse({'application': application1}, 'app-edit')


@pytest.mark.django_db
def test_org_reverse(organization1):
    assert org_reverse({'organization': organization1}, 'org-applications')


@pytest.mark.django_db
def test_order_formset(application1):
    Formset = inlineformset_factory(Organization,
                                    Application,
                                    fields=('name',),
                                    extra=1)
    fs = Formset(instance=application1.organization)
    ordered = [f.instance for f in order_formset(fs)]
    assert not ordered[0].pk
    assert ordered[1].pk


def test_render_serializer():
    assert render_serializer(Serializer())


def test_render_field():
    class TestSerializer(Serializer):
        test_field = Field()

    serializer = TestSerializer()
    field = serializer['test_field']

    assert render_field(field, {})
