import pytest
from strategy_field.utils import fqn

from bitcaster.dispatchers import Gmail

pytestmark = pytest.mark.django_db


def test_create_channel(django_app, organization1):
    owner = organization1.owner
    url = organization1.urls.channel_create
    res = django_app.get(url, user=owner.email)
    res.form['a-handler'] = fqn(Gmail)
    res = res.form.submit()
    assert res.status_code == 200, f"Submit failed with: {repr(res.context['form'].errors)}"

    res.form['b-name'] = 'PyTestChannel'
    res.form['username'] = 'example@gmail.com'
    res.form['password'] = '123'
    res.form['sender'] = 'example@gmail.com'
    res = res.form.submit()
    assert res.status_code == 302, f"Submit failed with: {repr(res.context['form'].errors)}"
    res = res.follow()
    channel = organization1.channels.filter(name='PyTestChannel').first()
    assert channel
    res = res.click(href=channel.urls.edit)
    res = res.form.submit()
    assert res.status_code == 302, f"Submit failed with: {repr(res.context['form'].errors)}"


def test_edit(django_app, channel1, admin_user):
    organization = channel1.organization
    owner = organization.owner
    url = channel1.urls.edit
    newvalue = channel1.config['timeout'] + 10
    res = django_app.get(url, user=owner.email)
    res.form['timeout'] = newvalue
    res = res.form.submit()
    assert res.status_code == 302, f"Submit failed with: {repr(res.context['form'].errors)}"
    channel1.refresh_from_db()
    assert channel1.config['timeout'] == newvalue


def test_deprecate(django_app, channel1):
    organization = channel1.organization
    owner = organization.owner
    res = django_app.get(organization.urls.channels, user=owner.email)
    res = res.click(href=channel1.urls.deprecate)
    assert res.status_code == 302, f"Submit failed with: {repr(res.context['form'].errors)}"
    channel1.refresh_from_db()
    assert channel1.deprecated


def test_toggle(django_app, channel1):
    organization = channel1.organization
    owner = organization.owner
    list_page = django_app.get(organization.urls.channels, user=owner.email)
    res = list_page.click(href=channel1.urls.toggle)
    assert res.status_code == 302, f"Submit failed with: {repr(res.context['form'].errors)}"
    channel1.refresh_from_db()
    assert not channel1.enabled

    res = list_page.click(href=channel1.urls.toggle)
    assert res.status_code == 302, f"Submit failed with: {repr(res.context['form'].errors)}"
    channel1.refresh_from_db()
    assert channel1.enabled


def test_test(django_app, subscription1):
    channel = subscription1.channel
    organization = channel.organization
    res = django_app.get(organization.urls.channels, user=subscription1.subscriber)
    res = res.click(href=channel.urls.test)
    assert res.status_code == 302, f"Submit failed with: {repr(res.context['form'].errors)}"


def test_test_no_address(django_app, channel1):
    organization = channel1.organization
    res = django_app.get(organization.urls.channels, user=organization.owner)
    res = res.click(href=channel1.urls.test)
    assert res.status_code == 302, f"Submit failed with: {repr(res.context['form'].errors)}"


def test_usage(django_app, channel1):
    organization = channel1.organization
    res = django_app.get(channel1.urls.usage, user=organization.owner)
    assert res.status_code == 200


# def test_info(django_app, channel1):
#     organization = channel1.organization
#     url = reverse('plugin-info', args=[fqn(channel1.handler)])
#     list_page = django_app.get(organization.urls.channels, user=organization.owner)
#     res = list_page.click(href=url)
#     assert res.status_code == 200
