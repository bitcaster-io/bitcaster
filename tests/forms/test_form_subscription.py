import pytest
from testutils.factories import AssignmentFactory, SubscriptionFactory

from bitcaster.forms.subscription import SubscriptionForm


@pytest.mark.django_db
def test_form_valid() -> None:
    subscription = SubscriptionFactory()
    other_assignment = AssignmentFactory()

    form = SubscriptionForm(
        {"notification": subscription.notification.pk, "assignment": other_assignment.pk, "active": True}
    )
    assert form.is_valid()
    assert form.cleaned_data["notification"] == subscription.notification


@pytest.mark.django_db
def test_form_rejects_duplicate() -> None:
    subscription = SubscriptionFactory()
    form = SubscriptionForm(
        {"notification": subscription.notification.pk, "assignment": subscription.assignment.pk, "active": True}
    )
    assert not form.is_valid()
    assert "A subscription for this notification and assignment already exists." in str(form.errors)


@pytest.mark.django_db
def test_form_allows_duplicate_when_editing_same_instance() -> None:
    subscription = SubscriptionFactory()
    form = SubscriptionForm(
        {
            "notification": subscription.notification.pk,
            "assignment": subscription.assignment.pk,
            "active": True,
        },
        instance=subscription,
    )
    assert form.is_valid()


@pytest.mark.django_db
def test_form_missing_assignment_skips_duplicate_check() -> None:
    subscription = SubscriptionFactory()
    form = SubscriptionForm({"notification": subscription.notification.pk, "active": True})
    assert not form.is_valid()
    assert "A subscription for this notification and assignment already exists." not in str(form.errors)
