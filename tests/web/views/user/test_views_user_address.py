import pytest
from django.urls import reverse

from bitcaster.models import Address

pytestmark = pytest.mark.django_db


def test_user_addresses(django_app, organization1, subscriber1):
    # UserAddressesView
    url = reverse('user-address', args=[organization1.slug])
    res = django_app.get(url, user=subscriber1)
    assert res.status_code == 200


def test_user_addresses_info(django_app, organization1, assignment1):
    url = reverse('user-address-info', args=[organization1.slug, assignment1.pk])
    res = django_app.get(url, user=assignment1.user)
    assert res


def test_user_addresses_delete(django_app, organization1, address1, ):
    url = reverse('user-address-delete', args=[organization1.slug,
                                               address1.pk])
    res = django_app.get(url, user=address1.user)
    res = res.form.submit()
    assert res.status_code == 302
    assert not Address.objects.filter(pk=address1.pk).exists()


def test_address_create(django_app, event1, assignment1):
    url = reverse('user-address-create', args=[event1.application.organization.slug])
    res = django_app.get(url, user=assignment1.user)
    res.form['label'] = 'Label'
    res.form['address'] = 'address'
    res.form['channels'] = [event1.channels.first().pk]
    res = res.form.submit()
    assert res.status_code == 302, f"Submit failed with: {repr(res.context['form'].errors)}"

# #
# # def test_user_addresses_duplicate(django_app, organization1, subscriber1):
# #     # UserAddressesView
# #     url = reverse('user-address', args=[organization1.slug])
# #     res = django_app.get(url, user=subscriber1)
# #     res.form.add_formset_field('addresses', {'label': 'aaaa', 'address': 'bbbb'})
# #     res.form['addresses-0-label'] = 'label'
# #     res.form['addresses-0-address'] = 'value'
# #     res.form['addresses-1-label'] = 'label'
# #     res.form['addresses-1-address'] = 'value'
# #     res = res.form.submit()
# #     assert 'Please correct the duplicate values below.' in str(res.body)
# #
# #
# # def test_user_addresses_unique(django_app, organization1, subscriber1):
# #     # UserAddressesView
# #     url = reverse('user-address', args=[organization1.slug])
# #     res = django_app.get(url, user=subscriber1)
# #     original = AddressFactory(user=subscriber1)
# #     res.form['addresses-0-label'] = original.label
# #     res.form['addresses-0-address'] = 'value'
# #     res = res.form.submit()
# #     assert 'Address with this User and Label already exists.' in str(res.body)
# #
#
# def test_user_assign_address(django_app, organization1, admin):
#     # UserAddressesAssignmentView
#     from bitcaster.utils.tests.factories import AddressFactory, ChannelFactory
#     address1 = AddressFactory(user=admin, address='+3912345678')
#     address2 = AddressFactory(user=admin, address='email@example.org')
#     address3 = AddressFactory(user=admin, address='email2@example.org')
#     address4 = AddressFactory(user=admin, address='email3@example.org')
#     channel1 = ChannelFactory(organization=organization1)
#     channel2 = ChannelFactory(organization=organization1)
#     url = reverse('user-address-assignment', args=[organization1.slug])
#     res = django_app.get(url, user=admin)
#     res = res.form.submit()
#     assert res.status_code == 200
#
#     res.form['assignments-0-channel'].force_value(channel1.pk)
#     res.form['assignments-0-address'].force_value(address1.pk)
#     res = res.form.submit()
#     assert res.status_code == 200
#
#     res.form['assignments-0-channel'].force_value(channel1.pk)
#     res.form['assignments-0-address'].force_value(address3.pk)
#     res.form.add_formset_field('assignments', {'channel': channel2.pk,
#                                                'address': address4.pk})
#     res = res.form.submit()
#
#     assert res.status_code == 302, f"Submit failed with: {repr(res.context['form'].errors)}"
#     assert admin.assignments.filter(user=admin,
#                                     channel=channel1,
#                                     address=address3).exists()
#
#     assert admin.assignments.filter(user=admin,
#                                     channel=channel2,
#                                     address=address4).exists()
#
#     url = reverse('user-address-assignment', args=[organization1.slug])
#     res = django_app.get(url, user=admin)
#     res.form['assignments-0-channel'].force_value(channel1.pk)
#     res.form['assignments-0-address'].force_value(address2.pk)
#     res = res.form.submit()
#     assert res.status_code == 302, f"Submit failed with: {repr(res.context['form'].errors)}"
#
#
# def test_user_address_assignment_delete(django_app, organization1, assignment1):
#     url = reverse('user-address-assignment', args=[organization1.slug])
#     res = django_app.get(url, user=organization1.owner)
#     res.form['assignments-0-DELETE'].checked = True
#     res = res.form.submit()
#     assert res.status_code == 302
#
#
# def test_user_address_verify_form(django_app, organization1, assignment1):
#     url = reverse('user-address-verify', args=[organization1.slug, assignment1.pk])
#     res = django_app.get(url, user=organization1.owner)
#     assert res.status_code == 200
#
#
# @pytest.mark.parametrize('verified', [True, False])
# def test_user_address_verify(django_app, organization1, assignment1, verified):
#     assignment1.address.verified = verified
#     assignment1.address.save()
#
#     url = reverse('user-address-verify', args=[organization1.slug, assignment1.pk])
#     res = django_app.get(url, user=organization1.owner)
#
#     token = res.form['csrfmiddlewaretoken'].value
#     django_app.set_cookie(settings.CSRF_COOKIE_NAME, token)
#
#     res = django_app.post(url, user=organization1.owner,
#                           params={'code': assignment1.address.code,
#                                   'csrfmiddlewaretoken': token})
#     assert res.status_code == 200
#
#
# def test_user_address_verify_fail(django_app, organization1, assignment1):
#     assignment1.address.verified = False
#     assignment1.address.save()
#
#     url = reverse('user-address-verify', args=[organization1.slug, assignment1.pk])
#     res = django_app.get(url, user=organization1.owner)
#
#     token = res.form['csrfmiddlewaretoken'].value
#     django_app.set_cookie(settings.CSRF_COOKIE_NAME, token)
#
#     res = django_app.post(url, user=organization1.owner,
#                           params={'code': 'abcdef',
#                                   'csrfmiddlewaretoken': token},
#                           expect_errors=True)
#     assert res.status_code == 400
#
#
# def test_user_verify_resend(django_app, organization1, assignment1):
#     # UserAddressesVerifyView
#     url = reverse('user-address-resend', args=[organization1.slug, assignment1.pk])
#     res = django_app.get(url, user=organization1.owner)
#     assert res
