import os

import pytest
from django.urls import reverse

from bitcaster.agents.handlers.imap import ImapAgent
from bitcaster.utils.reflect import fqn

pytestmark = pytest.mark.django_db


def test_monitor_list(django_app, monitor1, user1):
    application = monitor1.application
    organization = application.organization
    url = reverse('app-monitors', args=[organization.slug,
                                        application.slug])
    res_list = django_app.get(url, user=user1)
    assert monitor1.name in str(res_list.body)


def test_monitor_toggle(django_app, monitor1, user1):
    application = monitor1.application
    organization = application.organization
    url = reverse('app-monitor-toggle', args=[organization.slug,
                                              application.slug,
                                              monitor1.pk])
    res = django_app.get(url, user=user1).follow()
    assert res.status_code == 302
    monitor1.refresh_from_db()
    assert not monitor1.enabled


def test_monitor_test(django_app, monitor1, user1):
    application = monitor1.application
    organization = application.organization
    url = reverse('app-monitor-test', args=[organization.slug,
                                            application.slug,
                                            monitor1.pk])
    res = django_app.get(url, user=user1)
    assert res.status_code == 200


def test_monitor_update(django_app, monitor1, user1):
    application = monitor1.application
    organization = application.organization
    url = reverse('app-monitor-edit', args=[organization.slug,
                                            application.slug,
                                            monitor1.pk])
    res = django_app.get(url, user=user1)
    res = res.form.submit()
    assert res.status_code == 302, f"Submit failed with: {repr(res.context['form'].errors)}"


def test_monitor_delete(django_app, monitor1, user1):
    application = monitor1.application
    organization = application.organization
    url = reverse('app-monitor-delete', args=[organization.slug,
                                              application.slug,
                                              monitor1.pk])
    res = django_app.get(url, user=user1)
    res = res.form.submit()
    assert res.status_code == 302, f"Submit failed with: {repr(res.context['form'].errors)}"
    assert not application.monitors.filter(pk=monitor1.pk).exists()


def test_monitor_create(django_app, application1, event1):
    owner = application1.organization.owner
    url = application1.urls.monitor_create
    res = django_app.get(url, user=owner.email)
    res.form['a-handler'] = fqn(ImapAgent)
    res = res.form.submit()
    assert res.status_code == 200, f"Submit failed with: {repr(res.context['form'].errors)}"

    res.form['b-name'] = 'PyTestChannel'
    res.form['username'] = os.environ['TEST_MONITOR_USER']
    res.form['password'] = os.environ['TEST_MONITOR_PASSWORD']
    res.form['folder'] = os.environ['TEST_MONITOR_FOLDER']
    res.form['server'] = os.environ['TEST_MONITOR_SERVER']
    res.form['port'] = os.environ['TEST_MONITOR_PORT']
    res.form['tls'] = os.environ['TEST_MONITOR_TLS']
    res.form['policy'] = ImapAgent.options_class.READ
    res.form['event'] = event1.pk
    res = res.form.submit()
    assert res.status_code == 302, f"Submit failed with: {repr(res.context['form'].errors)}"
    res = res.follow()
    channel = application1.monitors.filter(name='PyTestChannel').first()
    assert channel
    res = res.click(href=channel.urls.edit)
    res = res.form.submit()
    assert res.status_code == 302, f"Submit failed with: {repr(res.context['form'].errors)}"
