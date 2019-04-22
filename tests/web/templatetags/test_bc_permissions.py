from unittest.mock import Mock

import pytest
from django.contrib.auth.models import AnonymousUser
from django.template import Context, Template, TemplateSyntaxError

pytestmark = pytest.mark.django_db


def render_template(string, context=None):
    context = context or {}
    context = Context(context)
    return Template(string).render(context)


def test_check_permissions_org(organization1):
    tpl = '{% load bc_permissions %}{% check_permissions organization %}{{permissions}}'
    request = Mock(user=organization1.owner)
    assert render_template(tpl, {'organization': organization1, 'request': request})


def test_check_permissions_app(application1):
    tpl = '{% load bc_permissions %}{% check_permissions application %}{{permissions}}'
    request = Mock(user=application1.organization.owner)
    assert render_template(tpl, {'application': application1, 'request': request})


def test_check_permissions_as(organization1):
    tpl = '{% load bc_permissions %}{% check_permissions org as perms %}{{perms.configure}}'
    request = Mock(user=organization1.owner)
    assert render_template(tpl, {'org': organization1, 'request': request})


def test_check_permissions_alien():
    tpl = '{% load bc_permissions %}{% check_permissions user %}{{permissions}}'
    request = Mock()
    assert render_template(tpl, {'user': Mock(), 'request': request})


@pytest.mark.parametrize('target', ['', 'aa bb'])
def test_check_permissions_invalid(target):
    tpl = '{%% load bc_permissions %%}{%% check_permissions %s %%}' % target
    request = Mock()
    with pytest.raises(TemplateSyntaxError):
        render_template(tpl, {'target': target, 'request': request})


@pytest.mark.parametrize('toggler', [None,
                                     True,
                                     False],
                         ids=['user', 'admin', 'anonymous'])
@pytest.mark.parametrize('user', [pytest.lazy_fixture('user1'),
                                  pytest.lazy_fixture('admin'),
                                  AnonymousUser()],
                         ids=['user', 'admin', 'anonymous'])
def test_button(organization1, user, toggler):
    tpl = '{{% load bc_permissions %}}' \
          '{{% check_permissions organization %}}' \
          '{{% button "" permissions.edit_channel "ic:ci" "enabled:disabled" {} %}}'.format(toggler)
    request = Mock()
    request.user = user
    assert render_template(tpl, {'request': request, 'organization': organization1})
