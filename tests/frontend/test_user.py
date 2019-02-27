import logging
from unittest import mock
from unittest.mock import Mock

import pytest
from constance.test import override_config
from django.urls import reverse

logger = logging.getLogger(__name__)

pytestmark = pytest.mark.django_db


@override_config(SYSTEM_CONFIGURED=0)
def test_owner_index_not_configured(django_app, organization1):
    # UserIndexView
    url = reverse('me', args=[organization1.slug])
    with mock.patch('bitcaster.system.system', Mock(configured=False)):
        res = django_app.get(url, user=organization1.owner)
    assert res.status_code == 200


@override_config(SYSTEM_CONFIGURED=0)
def test_admin_index_not_configured(django_app, organization1, admin):
    # UserIndexView
    url = reverse('me', args=[organization1.slug])
    with mock.patch('bitcaster.system.system', Mock(configured=False)):
        res = django_app.get(url, user=admin)
    assert res.status_code == 200


def test_user_index(django_app, subscription1, monkeypatch):
    # UserIndexView
    app = subscription1.channel.application
    org = app.organization
    url = reverse('me', args=[org.slug])
    res = django_app.get(url, user=org.owner)
    assert res.status_code == 200


def test_user_profile(django_app, admin):
    # UserProfileView
    url = reverse('user-profile')
    res = django_app.get(url, user=admin)
    res.form['friendly_name'] = 'Name'
    res.form['timezone'] = 'Europe/Rome'
    res.form['country'] = 'IT'
    res = res.form.submit()
    assert res.status_code == 302, f"Submit failed with: {repr(res.context['form'].errors)}"


def test_user_change_email(django_app, admin):
    # UserProfileView
    url = reverse('user-profile')
    res = django_app.get(url, user=admin)
    res.form['friendly_name'] = 'Name'
    res.form['email'] = 'new_email@example.com'
    res.form['timezone'] = 'Europe/Rome'
    res.form['country'] = 'IT'
    res = res.form.submit()
    assert res.status_code == 302, f"Submit failed with: {repr(res.context['form'].errors)}"
    res = django_app.get(url, user=admin)
    assert b'new email verification pending' in res.content


def test_user_addresses(django_app, admin):
    # UserAddressesView
    url = reverse('user-addresses')
    res = django_app.get(url, user=admin)
    # res.form.add_formset_field('addresses', {'label': 'aaaa', 'address': 'bbbb'})
    res.form['addresses-0-label'] = 'label'
    res.form['addresses-0-address'] = 'value'
    res = res.form.submit()
    assert res.status_code == 302, f"Submit failed with: {repr(res.context['form'].errors)}"
    assert admin.addresses.filter(label='label', address='value').exists()


def test_user_assign_address(django_app, admin):
    # UserAddressesAssignmentView
    from bitcaster.utils.tests.factories import AddressFactory, ChannelFactory
    address1 = AddressFactory(user=admin, address='+3912345678')
    address2 = AddressFactory(user=admin, address='email@example.org')
    channel1 = ChannelFactory()
    url = reverse('user-address-assignment')
    res = django_app.get(url, user=admin)
    res = res.form.submit()
    assert res.status_code == 200
    res.form['assignments-0-channel'] = channel1.pk
    res.form['assignments-0-address'] = address1.pk
    res = res.form.submit()
    assert res.status_code == 200

    res.form['assignments-0-address'] = address2.pk
    res = res.form.submit()
    assert res.status_code == 302, f"Submit failed with: {repr(res.context['form'].errors)}"
    assert admin.assignments.filter(user=admin,
                                    address=address2).exists()
