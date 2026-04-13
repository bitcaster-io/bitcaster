import pytest
from testutils.factories import AddressFactory, ChannelFactory, UserFactory

from bitcaster.forms.assignment import AssignmentInlineForm, DistributionListInlineForm


@pytest.mark.django_db
@pytest.mark.parametrize("form_class", [DistributionListInlineForm, AssignmentInlineForm])
def test_inline_form_init_with_user(form_class):
    user = UserFactory()
    address1 = AddressFactory(user=user)
    address2 = AddressFactory(user=user)
    AddressFactory()  # address for another user

    form = form_class(user=user)

    # Check if the address queryset is limited to the user's addresses
    queryset = list(form.fields["address"].queryset.order_by("pk"))
    expected = [address1, address2]
    # sort both to ensure comparison works regardless of order
    assert sorted([a.pk for a in queryset]) == sorted([a.pk for a in expected])
    assert sorted([a.pk for a in form.fields["address"].widget.queryset]) == sorted([a.pk for a in expected])


@pytest.mark.django_db
@pytest.mark.parametrize("form_class", [DistributionListInlineForm, AssignmentInlineForm])
def test_inline_form_init_without_user_pk(form_class):
    user = UserFactory.build()  # Not saved to DB, no PK
    form = form_class(user=user)

    # Check if the address queryset is empty as user.pk is None
    assert list(form.fields["address"].queryset) == []


@pytest.mark.django_db
@pytest.mark.parametrize("form_class", [DistributionListInlineForm, AssignmentInlineForm])
def test_inline_form_validation(form_class):
    user = UserFactory()
    address = AddressFactory(user=user)
    channel = ChannelFactory()

    data = {
        "address": address.pk,
        "channel": channel.pk,
    }
    form = form_class(data=data, user=user)
    assert form.is_valid()

    # Test with address not belonging to user
    other_address = AddressFactory()
    data["address"] = other_address.pk
    form = form_class(data=data, user=user)
    assert not form.is_valid()
    assert "address" in form.errors
