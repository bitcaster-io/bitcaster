import re

import pytest
from testutils.factories import (
    AssignmentFactory,
    ChannelFactory,
    DistributionListFactory,
    EventFactory,
    MessageTemplateFactory,
    NotificationFactory,
    SubscriptionFactory,
)
from testutils.helpers import assert_message
from testutils.perms import user_grant_permissions
from unittest.mock import patch

from django.urls import reverse

from bitcaster.cache.manager import CacheManager
from bitcaster.runner.tasks import (
    _check_distribution_lists,
    _check_events,
    _check_subscriptions,
    _message_template_fix_url,
    sanity_check,
)

pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def clear_sanity_cache():
    cm = CacheManager(None)
    for key in ("sanity:subscriptions", "sanity:distributionlists", "sanity:events", "sanity:state"):
        cm.delete(key)


def test_flow(django_app, user):
    channel = ChannelFactory()
    notification = NotificationFactory(event__channels=[channel], distribution=None)
    assignment = AssignmentFactory(channel=channel)
    SubscriptionFactory(notification=notification, assignment=assignment)

    sanity_check()

    url = reverse("admin:console-sanityview")
    with user_grant_permissions(user, ["bitcaster.console_tools"]):
        res = django_app.get(url, user=user)
    text = res.text

    fixes = re.findall(r'href="(/admin/bitcaster/messagetemplate/add/\?[^"]+)"[^>]*>Fix Issue', text)
    assert fixes, "no fix urls found"
    fix_url = fixes[0]
    with user_grant_permissions(user, ["bitcaster.console_tools", "bitcaster.add_messagetemplate"]):
        add = django_app.get(fix_url, user=user)
    frm = add.forms["messagetemplate_form"]
    assert frm["channel"].value == str(channel.pk)
    assert frm["event"].value == str(notification.event_id)
    assert frm["notification"].value == str(notification.pk)


def test_sanity_view_empty(django_app, user):
    url = reverse("admin:console-sanityview")
    with user_grant_permissions(user, ["bitcaster.console_tools"]):
        res = django_app.get(url, user=user)
    assert "No results yet" in res.text


def test_sanity_view_post(django_app, user):
    url = reverse("admin:console-sanityview")
    with user_grant_permissions(user, ["bitcaster.console_tools"]):
        res = django_app.get(url, user=user)
        res = res.forms["sanity_check"].submit("op").follow()
        assert_message(res, "Sanity check started")


def test_sanity_view_post_error(django_app, user):
    url = reverse("admin:console-sanityview")
    cm = CacheManager(None)
    with user_grant_permissions(user, ["bitcaster.console_tools"]):
        res = django_app.get(url, user=user)
        with patch("bitcaster.runner.tasks.sanity_check.send", side_effect=RuntimeError("boom")):
            with pytest.raises(RuntimeError, match="boom"):
                res.forms["sanity_check"].submit("op")
    assert cm.retrieve("sanity:state") is None


def test_sanity_view_post_without_op(django_app, user):
    url = reverse("admin:console-sanityview")
    with user_grant_permissions(user, ["bitcaster.console_tools"]):
        res = django_app.get(url, user=user)
        res = res.forms["sanity_check"].submit("op", value="other")
    assert res.status_code == 302


def test_tools_view_sanity_link(django_app, user):
    url = reverse("admin:console-toolsview")
    with user_grant_permissions(user, ["bitcaster.console_tools"]):
        res = django_app.get(url, user=user)
    assert "Run sanity check" in res.text

    sanity_check()

    with user_grant_permissions(user, ["bitcaster.console_tools"]):
        res = django_app.get(url, user=user)
    assert "View Sanity Check" in res.text


def test_tools_view_run_sanity_check(django_app, user):
    url = reverse("admin:console-toolsview")
    with user_grant_permissions(user, ["bitcaster.console_tools"]):
        res = django_app.get(url, user=user)
        res = res.forms["sanity_check"].submit("op").follow()
        assert_message(res, "Sanity check started")


def test_tools_view_scheduled_state(django_app, user):
    cm = CacheManager(None)
    cm.store("sanity:state", "scheduled", timeout=120, timeboxed=False)
    url = reverse("admin:console-toolsview")
    with user_grant_permissions(user, ["bitcaster.console_tools"]):
        res = django_app.get(url, user=user)
    assert "Sanity Check Scheduled" in res.text
    assert 'http-equiv="refresh"' in res.text


def test_tools_view_running_state(django_app, user):
    cm = CacheManager(None)
    cm.store("sanity:state", "running", timeout=120, timeboxed=False)
    url = reverse("admin:console-toolsview")
    with user_grant_permissions(user, ["bitcaster.console_tools"]):
        res = django_app.get(url, user=user)
    assert "Sanity Check Running" in res.text
    assert 'http-equiv="refresh"' in res.text


def test_sanity_view_groups_by_component(django_app, user):
    channel = ChannelFactory()
    event = EventFactory(channels=[channel])
    notification = NotificationFactory(event=event, distribution=None, active=True)
    assignment = AssignmentFactory(channel=channel)
    SubscriptionFactory(notification=notification, assignment=assignment)

    EventFactory(locked=True)

    sanity_check()

    url = reverse("admin:console-sanityview")
    with user_grant_permissions(user, ["bitcaster.console_tools"]):
        res = django_app.get(url, user=user)
    text = res.text

    assert "MessageTemplate (2)" in text
    m = text.index("MessageTemplate (")
    c = text.index("Channel (")
    e = text.index("Event (")
    assert m < c < e


def test_subscription_channel_not_enabled():
    channel = ChannelFactory()
    other = ChannelFactory()
    notification = NotificationFactory(event__channels=[other], distribution=None)
    assignment = AssignmentFactory(channel=channel)
    SubscriptionFactory(notification=notification, assignment=assignment)

    report = _check_subscriptions("ts")
    assert report["checked"] == 1
    assert len(report["invalid"]) == 1
    assert report["invalid"][0]["component"] == "Channel"
    assert not report["invalid"][0]["fix"]


def test_subscription_valid():
    channel = ChannelFactory()
    notification = NotificationFactory(event__channels=[channel], distribution=None)
    assignment = AssignmentFactory(channel=channel)
    SubscriptionFactory(notification=notification, assignment=assignment)
    MessageTemplateFactory(channel=channel, event=notification.event, notification=notification)

    report = _check_subscriptions("ts")
    assert report["checked"] == 1
    assert report["valid"] == 1
    assert report["invalid"] == []


def test_distribution_list_missing_message():
    dl = DistributionListFactory()
    channel = ChannelFactory()
    assignment = AssignmentFactory(channel=channel)
    dl.recipients.add(assignment)
    notification = NotificationFactory(event__channels=[channel], distribution=dl)

    report = _check_distribution_lists("ts")
    assert report["checked"] == 1
    assert len(report["invalid"]) == 1
    item = report["invalid"][0]
    assert item["component"] == "MessageTemplate"
    assert f"channel={channel.pk}" in item["fix"]
    assert f"notification={notification.pk}" in item["fix"]


def test_distribution_list_valid():
    dl = DistributionListFactory()
    channel = ChannelFactory()
    assignment = AssignmentFactory(channel=channel)
    dl.recipients.add(assignment)
    notification = NotificationFactory(event__channels=[channel], distribution=dl)
    MessageTemplateFactory(channel=channel, event=notification.event, notification=notification)

    report = _check_distribution_lists("ts")
    assert report["checked"] == 1
    assert report["invalid"] == []


def test_distribution_list_no_active_notifications_skipped():
    dl = DistributionListFactory(recipients=[AssignmentFactory()])
    NotificationFactory(distribution=dl, active=False)

    report = _check_distribution_lists("ts")
    assert report["checked"] == 0
    assert report["invalid"] == []


def test_message_template_fix_url_channel_only():
    channel = ChannelFactory()
    url = _message_template_fix_url(channel)
    assert f"channel={channel.pk}" in url
    assert "event=" not in url
    assert "notification=" not in url


def test_events_issues():
    from strategy_field.utils import fqn

    from bitcaster.dispatchers.email import EmailDispatcher

    broken = ChannelFactory(dispatcher=fqn(EmailDispatcher), config={})
    inactive = ChannelFactory(active=False)
    locked = ChannelFactory(locked=True)
    paused = ChannelFactory(paused=True)
    event = EventFactory(active=False, locked=True, paused=True, channels=[broken, inactive, locked, paused])
    event.application.active = False
    event.application.locked = True
    event.application.paused = True
    event.application.save()
    event.application.project.locked = True
    event.application.project.paused = True
    event.application.project.save()

    report = _check_events("ts")
    details = [i["detail"] for i in report["invalid"]]
    assert "Event is not active" in details
    assert "Event is locked" in details
    assert "Event is paused" in details
    assert "Application is not active" in details
    assert "Application is locked" in details
    assert "Application is paused" in details
    assert "Project is locked" in details
    assert "Project is paused" in details
    assert "No active notification for the event" in details
    assert "Channel is not active" in details
    assert "Channel is locked" in details
    assert "Channel is paused" in details
    assert "Invalid dispatcher configuration" in details
    assert any("Missing MessageTemplate" in d for d in details)


def test_event_no_channels():
    EventFactory()

    report = _check_events("ts")
    details = [i["detail"] for i in report["invalid"]]
    assert "No channel enabled for the event" in details
    assert "No active notification for the event" in details


def test_events_valid():
    channel = ChannelFactory()
    event = EventFactory(channels=[channel])
    notification = NotificationFactory(event=event, distribution=None, active=True)
    MessageTemplateFactory(channel=channel, event=event, notification=notification)

    report = _check_events("ts")
    assert report["checked"] == 1
    assert report["invalid"] == []


def test_events_dispatcher_config_raises():
    from django.core.exceptions import ValidationError
    from strategy_field.utils import fqn

    from bitcaster.dispatchers.email import EmailDispatcher

    channel = ChannelFactory(dispatcher=fqn(EmailDispatcher), config={})
    event = EventFactory(channels=[channel])
    NotificationFactory(event=event, distribution=None, active=True)
    MessageTemplateFactory(channel=channel, event=event, notification=event.notifications.first())

    with patch.object(EmailDispatcher, "config_class", side_effect=ValidationError("boom")):
        report = _check_events("ts")

    details = [i["detail"] for i in report["invalid"]]
    assert "Invalid dispatcher configuration" in details


def test_sanity_check_state_and_error():
    cm = CacheManager(None)
    sanity_check()
    assert cm.retrieve("sanity:state") == "done"
    assert cm.retrieve("sanity:subscriptions") is not None
    assert cm.retrieve("sanity:distributionlists") is not None
    assert cm.retrieve("sanity:events") is not None

    with patch("bitcaster.runner.tasks._check_subscriptions", side_effect=RuntimeError("boom")):
        with pytest.raises(RuntimeError, match="boom"):
            sanity_check()
    assert cm.retrieve("sanity:state") is None
