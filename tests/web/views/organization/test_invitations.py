import pytest
from django.urls import reverse

from bitcaster.models import Invitation
from bitcaster.security import ROLES
from bitcaster.utils.tests.environ import override_environ
from bitcaster.utils.tests.factories import (InvitationFactory,
                                             OrganizationGroupFactory,)

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize('emails', ['t1@a.com', 't0@a.com, t1@a.com'])
def test_invite_members(django_app, organization1, emails):
    group = OrganizationGroupFactory(organization=organization1)
    user = organization1.owner
    res = django_app.get(organization1.urls.invite, user=user)
    res.form['emails'] = emails
    res.form['groups'] = [group.pk]
    res.form['role'] = ROLES.MEMBER
    res = res.form.submit()
    assert res.status_code == 302, f"Submit failed with: {repr(res.context['form'].errors)}"
    res.follow()

    i = Invitation.objects.filter(target='t1@a.com',
                                  role=ROLES.MEMBER,
                                  organization=organization1).first()
    assert i
    assert list(i.groups.all()) == [group]


def test_invite_members_validate_emails(django_app, organization1):
    # url = reverse('user-autocomplete')
    user = organization1.owner
    res = django_app.get(organization1.urls.invite, user=user)
    res.form['emails'] = 'aaa'
    res.form['role'] = ROLES.MEMBER
    res = res.form.submit()
    assert res.status_code == 200
    assert res.context['form'].errors == {'emails': ['aaa is not a valid email address']}


@override_environ(BITCASTER_FAKE_OTP='1')
def test_invitation_accept(django_app, organization1):
    group = OrganizationGroupFactory(organization=organization1)

    invitation = InvitationFactory(organization=organization1,
                                   groups=[group],
                                   target='a@b.com')
    url = reverse('org-member-accept', args=[organization1.slug,
                                             invitation.pk,
                                             'otp'])
    res = django_app.get(url)
    res.form['friendly_name'] = 'friendly name'
    res.form['password1'] = 'password1'
    res.form['password2'] = 'password1'
    res = res.form.submit()
    assert res.status_code == 302, f"Submit failed with: {repr(res.context['form'].errors)}"
    assert organization1.memberships.filter(user__email='a@b.com',
                                            role=ROLES.MEMBER).exists()
    assert group.members.filter(user__email='a@b.com').exists()


@override_environ(BITCASTER_FAKE_OTP='1')
def test_invitation_email_exists(django_app, organization1):
    invitation = InvitationFactory(organization=organization1,
                                   target=organization1.owner.email)
    url = reverse('org-member-accept', args=[organization1.slug,
                                             invitation.pk,
                                             'otp'])
    res = django_app.get(url)
    assert res.status_code == 200
    assert b'Email used' in res.body


def test_invitation_expired(django_app, organization1):
    invitation = InvitationFactory(organization=organization1,
                                   target=organization1.owner.email)
    url = reverse('org-member-accept', args=[organization1.slug,
                                             invitation.pk,
                                             'otp'])
    res = django_app.get(url).follow()
    assert b'Invite expired' in res.body


@override_environ(BITCASTER_FAKE_OTP='1')
def test_invitation_invalid(django_app, organization1):
    url = reverse('org-member-accept', args=[organization1.slug,
                                             0,
                                             'otp'])
    res = django_app.get(url)
    assert res.status_code == 302
