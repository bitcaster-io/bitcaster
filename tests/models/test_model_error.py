import pytest
from django.core.exceptions import ObjectDoesNotExist

from bitcaster.models import ErrorEntry
from bitcaster.models.error import ErrorEvent


@pytest.mark.django_db
def test_create_organization(organization1):
    c = ErrorEntry(event=ErrorEvent.SUBSCRIPTION_ERROR,
                   organization=organization1,
                   target=None)
    c.clean()
    c.save()
    assert c.pk


@pytest.mark.django_db
def test_create_application(application1):
    c = ErrorEntry(event=ErrorEvent.SUBSCRIPTION_ERROR, application=application1)
    c.clean()
    c.save()
    assert c.pk


@pytest.mark.django_db
def test_create_target(event1):
    c = ErrorEntry(event=ErrorEvent.SUBSCRIPTION_ERROR, target=event1)
    c.clean()
    c.save()
    assert c.pk
    assert c.application == event1.application


@pytest.mark.django_db
def test_create_fail(subscription1):
    c = ErrorEntry(event=ErrorEvent.SUBSCRIPTION_ERROR, target=subscription1)
    with pytest.raises(ObjectDoesNotExist):
        c.save()
