import pytest


@pytest.mark.django_db
@pytest.mark.parametrize('value', [1, 'text', False, True, 1.1])
def test_org_option(organization1, value, settings):
    # settings.FERNET_KEYS = [b"a"]
    opt = organization1.options.create(key='org:test', value=value)
    assert opt.value == value

    opt = organization1.options.get(key='org:test')
    assert opt.value == value
