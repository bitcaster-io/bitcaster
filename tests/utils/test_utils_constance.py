import pytest
from constance.test import override_config
from django.core.exceptions import ValidationError

from bitcaster.utils.constance import (FieldMappingField, GroupChoiceField,
                                       LdapDNField, ObfuscatedInput,
                                       WriteOnlyInput, WriteOnlyTextarea,)


def test_utils_groupchoicefield():
    field = GroupChoiceField()
    assert field


# LdapDNField
@pytest.mark.parametrize('value', ['', None])
def test_ldapdnfield_required(value):
    field = LdapDNField(required=True)
    with pytest.raises(ValidationError):
        field.clean(value)


@pytest.mark.parametrize('value', ['', None])
def test_ldapdnfield_not_required(value):
    field = LdapDNField(required=False)
    assert not field.clean(value)


@pytest.mark.parametrize('value', ['key=value', 'key=', 'key=='])
def test_ldapdnfield_invalid(value):
    field = LdapDNField()
    with pytest.raises(ValidationError):
        field.clean(value)


@pytest.mark.parametrize('value', ['key=%(user)s', ])
def test_ldapdnfield_valid(value):
    field = LdapDNField()
    assert field.clean(value)


# FieldMappingField
@pytest.mark.parametrize('value', ['', None])
def test_FieldMappingField_required(value):
    field = FieldMappingField(required=True)
    with pytest.raises(ValidationError):
        field.clean(value)


@pytest.mark.parametrize('value', ['', None])
def test_fieldmappingfield_not_required(value):
    field = FieldMappingField(required=False)
    assert not field.clean(value)


@pytest.mark.parametrize('value', ['key=value', 'key:', 'key::'])
def test_fieldmappingfield_invalid(value):
    field = FieldMappingField()
    with pytest.raises(ValidationError):
        field.clean(value)


@pytest.mark.parametrize('value', ['key:value', ])
def test_fieldmappingfield_valid(value):
    field = FieldMappingField()
    assert field.clean(value)


@pytest.mark.parametrize('value', [{'a': 1}, str({'a': 1})])
def test_fieldmappingfield_prepare_value(value):
    field = FieldMappingField()
    assert field.prepare_value(value)


@pytest.mark.parametrize('value', [11, ''])
def test_fieldmappingfield_prepare_value_invalid(value):
    field = FieldMappingField()
    with pytest.raises(ValidationError):
        assert field.prepare_value(value)


# ObfuscatedInput
def test_obfuscatedinput():
    field = ObfuscatedInput()
    assert field.render('name', 'value')


# WriteOnlyTextarea
def test_writeonlytextarea():
    field = WriteOnlyTextarea()
    assert field.render('name', 'value')


@override_config(EMAIL_HOST_PASSWORD='abc')
def test_writeonlyinput():
    field = WriteOnlyInput()
    assert field.render('name', 'value')
    assert field.value_from_datadict({'EMAIL_HOST_PASSWORD': '***'}, {}, 'EMAIL_HOST_PASSWORD') == 'abc'
    assert field.value_from_datadict({'EMAIL_HOST_PASSWORD': '123'}, {}, 'EMAIL_HOST_PASSWORD') == '123'
