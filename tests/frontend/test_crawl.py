import pytest
from django.core import mail
from django.urls import reverse
from strategy_field.utils import fqn

from bitcaster.dispatchers import Email
from bitcaster.models import Channel

pytestmark = pytest.mark.django_db


def test_initial_setup(django_app, application1):
    "home is always accessible"
    organization = application1.organization
    owner = organization.owner

    res = django_app.get('/', user=owner.email).follow()
    # res = res.click("Login")
    # res.form["username"] = owner.email
    # res.form["password"] = owner._password
    # res = res.form.submit().follow()
    #
    # res = res.click(organization.name)
    res = res.click("Configuration")
    res.form["slug"] = "org_slug"
    res.form["billing_email"] = "billing@noreply.org"
    res = res.form.submit().follow()
    #   channels
    res = res.click("Channels")

    #   channels
    res = res.click("Members")

    #   applications
    res = res.click("Applications")
    res = res.click("Create new application")
    res.form["name"] = "Application1"
    res = res.form.submit().follow()
    # now we are in Application screen
    # go beck to Organization
    res = res.click(f"\[{organization.name}\]")

    # invite someone
    res = res.click("Members")
    res = res.click("Invite members")
    res.form['memberships-0-email'] = 'user1@example.org'
    res = res.form.submit().follow()

    assert len(mail.outbox) == 1
    assert mail.outbox[0].subject == '[Bitcaster] invitation'

    # html = HTML(html=mail.outbox[0].alternatives[0][0])
    # link = html.find('a[class~=confirmation]')[0]
    # url = link.attrs['href']
    # res = django_app.get(url)
    # assert 'Create application' in str(res.content)


def test_organization_channels_wizard(django_app, organization1):
    res = django_app.get('/', user=organization1.owner).follow()
    res = res.click("Channels")
    res = res.click("Create channel")

    res.form['a-handler'] = fqn(Email)
    res = res.form.submit()
    res.form['b-name'] = 'Channel1'
    res = res.form.submit()

    res.form['username'] = 'username'
    res.form['password'] = 'password'
    res.form['server'] = 'localhost'
    res.form['port'] = '24'
    res.form['sender'] = 'me@example.com'
    res = res.form.submit().follow()

    channel = Channel.objects.filter(name='Channel1',
                                     organization=organization1,
                                     system=False).first()
    assert channel
    assert channel.config['username'] == 'username'
    assert channel.config['password'] == 'password'
    assert channel.config['server'] == 'localhost'


def test_organization_list_channel(django_app, org_channel):
    _list = django_app.get(reverse('org-channel-list',
                                   args=[org_channel.organization.slug]),
                           user=org_channel.organization.owner)

    res = _list.click("Hide").follow()
    org_channel.refresh_from_db()
    assert org_channel.deprecated
    res = res.click("Show").follow()
    org_channel.refresh_from_db()
    assert not org_channel.deprecated

    res = _list.click("Disable").follow()
    org_channel.refresh_from_db()
    assert not org_channel.enabled
    res = res.click("Enable")
    org_channel.refresh_from_db()
    assert org_channel.enabled

    res = _list.click("Remove")
    res = res.form.submit().follow()
    with pytest.raises(Channel.DoesNotExist):
        assert not org_channel.refresh_from_db()
