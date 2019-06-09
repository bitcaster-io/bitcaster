import base64
from unittest.mock import Mock
from uuid import uuid4

from bitcaster.framework.db.fields import (ORG_ROLES, AgentField,
                                           DispatcherField, EncryptedJSONField,
                                           OrganizationRoleField,)


def get_key():
    return base64.urlsafe_b64encode(uuid4().hex.encode()[:32])


def test_encryptedjsonfield_nosettings(settings):
    settings.SECRET_KEY = uuid4().hex
    settings.FERNET_KEYS = None
    settings.FERNET_USE_HKDF = None
    f = EncryptedJSONField()
    assert f.keys
    assert f.fernet_keys
    assert f.fernet


def test_encryptedjsonfield_multiple(settings):
    settings.FERNET_KEYS = [get_key(), get_key()]
    settings.FERNET_USE_HKDF = None
    f = EncryptedJSONField()
    assert f.keys
    assert f.fernet_keys
    assert f.fernet


def test_encryptedjsonfield():
    f = EncryptedJSONField()
    assert f.keys
    assert f.fernet_keys
    assert f.fernet
    v = f.get_prep_value({'a': '123'})
    assert v
    assert f.from_db_value(v.adapted, None, None, None)


def test_DispatcherField_eq():
    f = DispatcherField()
    assert not f == 2


def test_AgentField_eq():
    f = AgentField()
    assert not f == 2


def test_RoleField():
    f = OrganizationRoleField()
    f.attname = 'attr'
    assert f.value_to_string(Mock(attr=1)) == '1'
    assert f.get_prep_value(ORG_ROLES.OWNER) == 1
