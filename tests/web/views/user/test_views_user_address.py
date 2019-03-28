import pytest
from django.urls import reverse

from bitcaster.utils.tests.factories import AddressFactory

pytestmark = pytest.mark.django_db


def test_user_addresses(django_app, organization1, subscriber1):
    # UserAddressesView
    url = reverse('user-address', args=[organization1.slug])
    res = django_app.get(url, user=subscriber1)
    res.form.add_formset_field('addresses', {'label': 'aaaa', 'address': 'bbbb'})
    res.form['addresses-0-label'] = 'label'
    res.form['addresses-0-address'] = 'value'
    res.form['addresses-1-label'] = 'label1'
    res.form['addresses-1-address'] = 'value1'
    res = res.form.submit()
    assert res.status_code == 302, f"Submit failed with: {repr(res.context['form'].errors)}"
    assert subscriber1.addresses.filter(label='label', address='value').exists()
    assert subscriber1.addresses.filter(label='label1', address='value1').exists()


def test_user_addresses_info(django_app, organization1, assignment1, ):
    url = reverse('user-address-info', args=[organization1.slug, assignment1.pk])
    res = django_app.get(url, user=assignment1.user)
    assert res


def test_user_addresses_duplicate(django_app, organization1, subscriber1):
    # UserAddressesView
    url = reverse('user-address', args=[organization1.slug])
    res = django_app.get(url, user=subscriber1)
    res.form.add_formset_field('addresses', {'label': 'aaaa', 'address': 'bbbb'})
    res.form['addresses-0-label'] = 'label'
    res.form['addresses-0-address'] = 'value'
    res.form['addresses-1-label'] = 'label'
    res.form['addresses-1-address'] = 'value'
    res = res.form.submit()
    assert 'Please correct the duplicate values below.' in str(res.body)


def test_user_addresses_unique(django_app, organization1, subscriber1):
    # UserAddressesView
    url = reverse('user-address', args=[organization1.slug])
    res = django_app.get(url, user=subscriber1)
    original = AddressFactory(user=subscriber1)
    res.form['addresses-0-label'] = original.label
    res.form['addresses-0-address'] = 'value'
    res = res.form.submit()
    assert 'Address with this User and Label already exists.' in str(res.body)


def test_user_assign_address(django_app, organization1, admin):
    # UserAddressesAssignmentView
    from bitcaster.utils.tests.factories import AddressFactory, ChannelFactory
    address1 = AddressFactory(user=admin, address='+3912345678')
    address2 = AddressFactory(user=admin, address='email@example.org')
    channel1 = ChannelFactory()
    url = reverse('user-address-assignment', args=[organization1.slug])
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
