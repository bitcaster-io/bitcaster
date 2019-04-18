
import pytest
from django.core.exceptions import ValidationError

from bitcaster.models.invitation import Invitation
from bitcaster.utils.tests.factories import InvitationFactory

pytestmark = pytest.mark.django_db


def test_create_with_organization1(organization1):
    i = Invitation(organization=organization1)
    i.save()
    assert i.organization == organization1


def test_create_with_application(application1):
    i = Invitation(application=application1)
    i.save()
    assert i.organization == i.application.organization


def test_create_with_event(event1):
    i = Invitation(event=event1)
    i.save()
    assert i.application == event1.application
    assert i.organization == event1.application.organization


def test_create_invalid(event1):
    i = Invitation()
    with pytest.raises(ValidationError):
        i.save()


def test_str(event1):
    i = Invitation(target='test')
    assert str(i)


def test_send_email(organization1):
    i = InvitationFactory(organization=organization1, target='test@noreply.com')
    assert i.send_email().result == 1
