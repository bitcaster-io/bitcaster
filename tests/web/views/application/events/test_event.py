import pytest
from django.urls import reverse

from bitcaster.models import Channel, DispatcherMetaData
from bitcaster.utils.reflect import fqn
from bitcaster.utils.tests.factories import EventFactory, MessageFactory

pytestmark = pytest.mark.django_db


def test_event_list(django_app, event1, user1):
    application = event1.application
    organization = application.organization
    url = reverse('app-events', args=[organization.slug,
                                      application.slug])
    res_list = django_app.get(url, user=user1)
    assert event1.name in str(res_list.body)
    res_list.click(href='/%d/messages' % event1.pk)
    res_list.click(href='/%d/edit' % event1.pk)
    res_list.click(href='/%d/toggle' % event1.pk)
    res_list.click(href='/%d/delete' % event1.pk)
    res_list.click(href='/%d/test' % event1.pk)
    res_list.click(href='/%d/keys' % event1.pk)
    res_list.click(href='/%d/bee' % event1.pk)


# @pytest.mark.parametrize("url", )
#
# def test_event_buttons(django_app, event1, user1):
#     application = event1.application
#     organization = application.organization
#     url = reverse('app-events', args=[organization.slug,
#                                       application.slug])
#     res_list = django_app.get(url, user=user1)
#     for op in ['edit']:
#         url = reverse('app-event-%s' % op, args=event1.pk)
#         res_list.click(href='/%d/messages' % event1.pk)


def test_event_toggle_fail(django_app, event1, user1):
    application = event1.application
    organization = application.organization
    url = reverse('app-event-toggle', args=[organization.slug,
                                            application.slug,
                                            event1.pk])
    res = django_app.get(url, user=user1).follow()
    assert res.status_code == 200
    assert 'No messages configured for this event. Cannot be enabled' in str(res.body)


def test_event_toggle(django_app, message1, user1):
    event = message1.event
    application = event.application
    organization = application.organization
    url = reverse('app-event-toggle', args=[organization.slug,
                                            application.slug,
                                            event.pk])
    django_app.get(url, user=user1).follow()
    event.refresh_from_db()
    assert not event.enabled

    django_app.get(url, user=user1).follow()
    event.refresh_from_db()
    assert event.enabled


def test_event_cannot_enable_if_no_enabled_messages(django_app, channel1, user1):
    event1 = EventFactory(application=channel1.application, enabled=False)
    event1.channels.add(channel1)

    MessageFactory(event=event1,
                   channel=event1.channels.first(),
                   enabled=False)
    application = event1.application
    organization = application.organization
    url = reverse('app-event-toggle', args=[organization.slug,
                                            application.slug,
                                            event1.pk])
    res = django_app.get(url, user=user1).follow()
    assert 'No messages enabled for this event. Cannot be enabled' in str(res.body)

    event1.refresh_from_db()
    assert not event1.enabled


def test_event_cannot_enable_if_no_valid_messages(django_app, channel1, user1):
    event1 = EventFactory(application=channel1.application, enabled=False)
    event1.channels.add(channel1)

    MessageFactory(event=event1,
                   body='',
                   channel=event1.channels.first(),
                   enabled=True)
    application = event1.application
    organization = application.organization
    url = reverse('app-event-toggle', args=[organization.slug,
                                            application.slug,
                                            event1.pk])
    res = django_app.get(url, user=user1).follow()
    assert b'message does not validate' in res.body

    event1.refresh_from_db()
    assert not event1.enabled


def test_event_test(django_app, event1, user1):
    application = event1.application
    organization = application.organization
    url = reverse('app-event-test', args=[organization.slug,
                                          application.slug,
                                          event1.pk])
    res = django_app.get(url, user=user1)
    assert b'Warning new key has been created' not in res.body


def test_event_update(django_app, event1, user1, monkeypatch):
    monkeypatch.setattr('%s.objects.enabled' % fqn(DispatcherMetaData),
                        lambda: DispatcherMetaData.objects.all())
    monkeypatch.setattr('%s.objects.selectable' % fqn(Channel),
                        lambda *a, **k: Channel.objects.all())

    application = event1.application
    organization = application.organization
    url = reverse('app-event-edit', args=[organization.slug,
                                          application.slug,
                                          event1.pk])
    res = django_app.get(url, user=user1)
    res.form['channels'].force_value([str(a.pk) for a in event1.channels.all()])
    res = res.form.submit()
    assert res.status_code == 302, f"Submit failed with: {repr(res.context['form'].errors)}"


def test_event_delete(django_app, event1, user1):
    application = event1.application
    organization = application.organization
    url = reverse('app-event-delete', args=[organization.slug,
                                            application.slug,
                                            event1.pk])
    res = django_app.get(url, user=user1)
    res = res.form.submit()
    assert res.status_code == 302, f"Submit failed with: {repr(res.context['form'].errors)}"
    assert not application.events.filter(pk=event1.pk).exists()


def test_event_create(django_app, channel1, user1, monkeypatch):
    monkeypatch.setattr('%s.objects.selectable' % fqn(Channel),
                        lambda *a, **k: Channel.objects.all())

    application = channel1.application
    organization = application.organization
    url = reverse('app-event-create', args=[organization.slug,
                                            application.slug])
    res = django_app.get(url, user=user1)
    res.form['name'] = 'TestEvent1'
    res.form['channels'].force_value(channel1.pk)

    res = res.form.submit()
    assert res.status_code == 302, f"Submit failed with: {repr(res.context['form'].errors)}"

    res = django_app.get(url, user=user1)
    res.form['name'] = 'TestEvent2'
    res.form['channels'].force_value(channel1.pk)
    res = res.form.submit('save_edit_messages')
    assert res.status_code == 302, f"Submit failed with: {repr(res.context['form'].errors)}"
