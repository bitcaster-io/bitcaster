import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


# UserAutocomplete
def test_userautocomplete_full(django_app, organization1):
    url = reverse('user-autocomplete')
    user = organization1.owner
    res = django_app.get(url, user=user)
    assert res.json['results'][0]['text'] == user.email


def test_userautocomplete_query(django_app, organization1):
    url = reverse('user-autocomplete')
    user = organization1.owner

    url = '%s?q=%s' % (url, user.email)
    res = django_app.get(url, user=user)
    assert res.json['results'][0]['text'] == user.email


def test_userautocomplete_anonymous(django_app, organization1):
    url = reverse('user-autocomplete')
    user = organization1.owner

    url = '%s?q=%s' % (url, user.email)
    res = django_app.get(url)
    assert res.status_code != 200  # now 302 should be 401 ?


# ChannelAutocomplete
def test_channelautocomplete_full(django_app, channel1):
    url = reverse('channel-autocomplete')
    organization = channel1.organization
    user = organization.owner
    res = django_app.get(url, user=user)
    assert res.json['results'][0]['text'] == channel1.name


def test_channelautocomplete_query(django_app, channel1):
    url = reverse('channel-autocomplete')
    organization = channel1.organization
    user = organization.owner

    url = '%s?q=%s' % (url, channel1.name)
    res = django_app.get(url, user=user)
    assert res.json['results'][0]['text'] == channel1.name


def test_channelautocomplete_anonymous(django_app, channel1):
    url = reverse('channel-autocomplete')
    organization = channel1.organization
    user = organization.owner

    url = '%s?q=%s' % (url, user.email)
    res = django_app.get(url)
    assert res.status_code != 200  # now 302 should be 401 ?


# AddressAutocomplete

def test_addressautocomplete_full(django_app, organization_member):
    url = reverse('address-autocomplete')
    user = organization_member.user

    res = django_app.get(url, user=user)
    assert res.json['results'][0]['text'] == str(user.addresses.first())


def test_addressautocomplete_query(django_app, organization_member):
    url = reverse('address-autocomplete')
    user = organization_member.user

    url = '%s?q=%s' % (url, user.addresses.first().label)
    res = django_app.get(url, user=user)
    assert res.json['results'][0]['text'] == str(user.addresses.first())


# ApplicationAutocomplete

def test_applicationutocomplete_full(django_app, application1):
    url = reverse('application-autocomplete', args=[application1.organization.slug])
    user = application1.organization.owner

    res = django_app.get(url, user=user)
    assert res.json['results'][0]['text'] == application1.name


def test_applicationautocomplete_query(django_app, application1):
    url = reverse('application-autocomplete', args=[application1.organization.slug])
    user = application1.organization.owner

    url = '%s?q=%s' % (url, application1.name)
    res = django_app.get(url, user=user)
    assert res.json['results'][0]['text'] == application1.name


# OrganizationMembersAutocomplete

def test_organization_memberautocomplete_full(django_app, organization_member):
    url = reverse('org-member-autocomplete', args=[organization_member.organization.slug])
    user = organization_member.organization.owner
    res = django_app.get(url, user=user)
    assert res.json['results'][0]['text'] == str(user)


def test_organization_memberautocomplete_query(django_app, organization_member):
    url = reverse('org-member-autocomplete', args=[organization_member.organization.slug])
    user = organization_member.user

    url = '%s?q=%s' % (url, user.email)
    res = django_app.get(url, user=user)
    assert res.json['results'][0]['text'] == str(user)


# ApplicationMembersAutocomplete

def test_application_memberautocomplete_full(django_app, application_member):
    url = reverse('app-member-autocomplete', args=[application_member.application.organization.slug,
                                                   application_member.application.slug])
    user = application_member.application.organization.owner
    res = django_app.get(url, user=user)
    assert res.json['results'][0]['text'] == str(user)


def test_application_memberautocomplete_query(django_app, application_member):
    url = reverse('app-member-autocomplete', args=[application_member.application.organization.slug,
                                                   application_member.application.slug])
    user = application_member.application.organization.owner

    url = '%s?q=%s' % (url, str(user))
    res = django_app.get(url, user=user)
    assert res.json['results'][0]['text'] == str(user)


# ApplicationCandidateAutocomplete

def test_application_candidate_autocomplete_full(django_app, application1, organization_member):
    url = reverse('app-candidate-autocomplete', args=[application1.organization.slug,
                                                      application1.slug])
    user = application1.organization.owner
    res = django_app.get(url, user=user)
    assert res.json['results'][0]['text'] == str(user)


def test_application_candidate_autocomplete_query(django_app, application1, organization_member):
    url = reverse('app-candidate-autocomplete', args=[application1.organization.slug,
                                                      application1.slug])
    user = application1.organization.owner

    url = '%s?q=%s' % (url, user.email)
    res = django_app.get(url, user=user)
    assert res.json['results'][0]['text'] == str(user)
