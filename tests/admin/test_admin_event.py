from typing import TYPE_CHECKING, TypedDict

import pytest

from django.contrib.admin.templatetags.admin_urls import admin_urlname
from django.contrib.messages import SUCCESS, Message  # type: ignore[attr-defined]
from django.urls import reverse

from bitcaster.constants import bitcaster

if TYPE_CHECKING:
    from django.db.models.options import Options
    from django_webtest import DjangoTestApp
    from django_webtest.pytest_plugin import MixinWithInstanceVariables

    from bitcaster.models import Application, Assignment, Channel, Event, Notification, User

    Context = TypedDict(
        "Context",
        {
            "channel": Channel,
            "event": Event,
            "assignment": Assignment,
        },
    )


@pytest.fixture
def app(django_app_factory: "MixinWithInstanceVariables", admin_user: "User") -> "DjangoTestApp":
    django_app = django_app_factory(csrf_checks=False)
    django_app.set_user(admin_user)
    django_app._user = admin_user
    return django_app


@pytest.fixture
def context(app: "DjangoTestApp") -> "Context":
    from testutils.factories import AssignmentFactory, NotificationFactory

    asm: "Assignment" = AssignmentFactory(address__user=app._user)
    n: "Notification" = NotificationFactory(distribution__recipients=[asm], event__channels=[asm.channel])

    return {
        "channel": asm.channel,
        "assignment": asm,
        "event": n.event,
    }


def test_add_event(app: "DjangoTestApp", application: "Application") -> None:
    url = reverse("admin:bitcaster_event_add")
    res = app.get(url)
    res.forms["event_form"]["name"] = "Event #1"
    res.forms["event_form"]["application"].force_value(application.pk)
    res.forms["event_form"]["application"].force_value(application.pk)
    res = res.forms["event_form"].submit()
    assert res.status_code == 302


def test_add_event_shows_save_and_continue(app: "DjangoTestApp", application: "Application") -> None:
    url = reverse("admin:bitcaster_event_add")
    res = app.get(url)
    # two-step create: "Save and continue editing" is the only submit button on the add page
    assert res.pyquery("#submit-row [name=_continue]")
    assert not res.pyquery("#submit-row [name=_save]")
    assert not res.pyquery("#submit-row [name=_addanother]")
    assert not res.pyquery("#submit-row [name=_saveasnew]")


def test_change_event_shows_save(app: "DjangoTestApp", event: "Event") -> None:
    url = reverse("admin:bitcaster_event_change", args=[event.pk])
    res = app.get(url)
    assert res.pyquery("#submit-row [name=_save]")
    assert res.pyquery("#submit-row [name=_continue]")


def test_change_event(app: "DjangoTestApp", event: "Event") -> None:
    url = reverse("admin:bitcaster_event_change", args=[event.pk])
    res = app.get(url)
    res.forms["event_form"]["description"] = "Event #2"
    res = res.forms["event_form"].submit()
    assert res.status_code == 302


def test_trigger_event(app: "DjangoTestApp", context: "Context") -> None:
    event: Event = context["event"]
    opts: "Options[Event]" = event._meta
    url = reverse(admin_urlname(opts, "trigger_event"), args=[event.pk])  # type: ignore[arg-type]
    res = app.post(url, {})
    assert res.status_code == 200

    res = app.get(url)
    assert res.status_code == 200
    res.forms["test-form"]["assignment"] = context["assignment"].pk
    res = res.forms["test-form"].submit().follow()

    assert len(res.context["messages"]) == 1
    msg: Message = list(res.context["messages"])[0]
    assert msg.level == SUCCESS


def test_trigger_event_permission_required(app: "DjangoTestApp", context: "Context") -> None:
    from bitcaster.models import User

    event: Event = context["event"]
    user: User = User.objects.create_user("limited@example.com", password="p", is_staff=True)
    app.set_user(user)
    opts: "Options[Event]" = event._meta
    url = reverse(admin_urlname(opts, "trigger_event"), args=[event.pk])  # type: ignore[arg-type]
    res = app.get(url, expect_errors=True)
    assert res.status_code == 403


def test_debug_event_permission_required(app: "DjangoTestApp", context: "Context") -> None:
    from bitcaster.models import User

    event: Event = context["event"]
    user: User = User.objects.create_user("limited2@example.com", password="p", is_staff=True)
    app.set_user(user)
    opts: "Options[Event]" = event._meta
    url = reverse(admin_urlname(opts, "debug_event"), args=[event.pk])  # type: ignore[arg-type]
    res = app.get(url, expect_errors=True)
    assert res.status_code == 403


def test_delete_event(app: "DjangoTestApp", context: "Context") -> None:
    from bitcaster.models import Event

    event: "Event" = context["event"]
    opts: "Options[Event]" = event._meta
    url = reverse(admin_urlname(opts, "change"), args=[event.pk])  # type: ignore[arg-type]
    res = app.get(url, {})
    res = res.click("Delete")
    delete_form_index = next(filter(lambda i: res.forms[i].action == "", res.forms))
    res.forms[delete_form_index].submit().follow()
    assert not Event.objects.filter(pk=event.pk).exists()


def test_delete_event_protect_internal(app: "DjangoTestApp", context: "Context") -> None:
    from testutils.factories import EventFactory

    internal_event: Event = EventFactory(
        application__name=bitcaster.APPLICATION,
        application__project__name=bitcaster.PROJECT,
        application__project__organization__name=bitcaster.ORGANIZATION,
    )
    url = reverse("admin:bitcaster_event_change", args=[internal_event.pk])  # type: ignore[arg-type]
    res = app.get(url, {})
    with pytest.raises(IndexError):
        res.click("Delete")


def test_delete_action(app: "DjangoTestApp", context: "Context") -> None:
    from testutils.factories import EventFactory

    from bitcaster.models import Event

    event: "Event" = context["event"]
    internal_event: Event = EventFactory(
        application__name=bitcaster.APPLICATION,
        application__project__name=bitcaster.PROJECT,
        application__project__organization__name=bitcaster.ORGANIZATION,
    )
    url = reverse("admin:bitcaster_event_changelist")  # type: ignore[arg-type]
    res = app.get(url, {})
    frm = res.forms["changelist-form"]
    frm.get("_selected_action", index=0).checked = True
    frm.get("_selected_action", index=1).checked = True
    frm.get("action").value = "delete_selected"

    res = frm.submit()
    assert "Are you sure you want to delete the selected events?" in res.text
    delete_form_index = next(filter(lambda i: res.forms[i].action == "", res.forms))
    res.forms[delete_form_index].submit().follow()
    assert not Event.objects.filter(pk=event.pk).exists()
    assert Event.objects.filter(pk=internal_event.pk).exists()


@pytest.fixture
def debug_context(app: "DjangoTestApp") -> "Context":
    from testutils.factories import AssignmentFactory, MessageTemplateFactory, NotificationFactory

    asm: "Assignment" = AssignmentFactory(address__user=app._user)
    n: "Notification" = NotificationFactory(
        distribution__recipients=[asm], event__channels=[asm.channel], payload_filter="foo=='bar'"
    )
    MessageTemplateFactory(channel=asm.channel, event=n.event, content="Hello {{ foo }}")
    return {
        "channel": asm.channel,
        "assignment": asm,
        "event": n.event,
    }


def test_debug_event_get(app: "DjangoTestApp", debug_context: "Context") -> None:
    from bitcaster.models import Occurrence

    event: "Event" = debug_context["event"]
    opts: "Options[Event]" = event._meta
    url = reverse(admin_urlname(opts, "debug_event"), args=[event.pk])  # type: ignore[arg-type]
    res = app.get(url)
    assert res.status_code == 200
    assert "debug-form" in res.text
    assert res.pyquery("#id_context") is not None
    assert res.pyquery("#id_mode") is not None
    assert res.pyquery("#id_limit_to") is not None
    assert "Emulate API call" in res.text
    assert "tab-wrapper" in res.text
    assert "fieldset-emulate-api-call" in res.text
    assert "fieldset-general" in res.text
    assert Occurrence.objects.count() == 0


def test_debug_event_sync_fast(app: "DjangoTestApp", debug_context: "Context") -> None:
    from bitcaster.models import EventSimulation, Occurrence

    event: "Event" = debug_context["event"]
    opts: "Options[Event]" = event._meta
    url = reverse(admin_urlname(opts, "debug_event"), args=[event.pk])  # type: ignore[arg-type]
    res = app.post(url, {"context": '{"foo": "bar"}', "mode": "fast"}).follow()
    assert res.status_code == 200
    assert debug_context["assignment"].address.value in res.text
    assert 'id="preview-' not in res.text  # no rendered content in fast mode
    assert Occurrence.objects.count() == 0  # no occurrence rows created
    simulation = EventSimulation.objects.get()
    assert simulation.status == Occurrence.Status.PROCESSING.value
    assert simulation.mode == "fast"
    assert simulation.context == {"foo": "bar"}


def test_debug_event_sync_full_runs_background(app: "DjangoTestApp", debug_context: "Context") -> None:
    from unittest.mock import patch

    from bitcaster.models import EventSimulation, Occurrence

    event: "Event" = debug_context["event"]
    opts: "Options[Event]" = event._meta
    url = reverse(admin_urlname(opts, "debug_event"), args=[event.pk])  # type: ignore[arg-type]
    with patch("bitcaster.admin.event.run_event_simulation.send") as mock_send:
        res = app.post(url, {"context": '{"foo": "bar"}', "mode": "full"})
    assert res.status_code == 302
    simulation = EventSimulation.objects.get()
    assert simulation.status == Occurrence.Status.NEW.value
    assert simulation.mode == "full"
    mock_send.assert_called_once_with(simulation.pk)
    assert f"simulation={simulation.pk}" in res["Location"]


def test_debug_event_sync_partial_runs_background(app: "DjangoTestApp", debug_context: "Context") -> None:
    from unittest.mock import patch

    from bitcaster.models import EventSimulation, Occurrence

    event: "Event" = debug_context["event"]
    opts: "Options[Event]" = event._meta
    url = reverse(admin_urlname(opts, "debug_event"), args=[event.pk])  # type: ignore[arg-type]
    with patch("bitcaster.admin.event.run_event_simulation.send") as mock_send:
        res = app.post(url, {"context": '{"foo": "bar"}', "mode": "partial"})
    assert res.status_code == 302
    simulation = EventSimulation.objects.get()
    assert simulation.status == Occurrence.Status.NEW.value
    assert simulation.mode == "partial"
    mock_send.assert_called_once_with(simulation.pk)


def test_debug_event_payload_filter(app: "DjangoTestApp", debug_context: "Context") -> None:
    from bitcaster.models import EventSimulation, Occurrence

    event: "Event" = debug_context["event"]
    opts: "Options[Event]" = event._meta
    url = reverse(admin_urlname(opts, "debug_event"), args=[event.pk])  # type: ignore[arg-type]
    res = app.post(url, {"context": '{"foo": "dummy"}', "mode": "fast"}).follow()
    assert res.status_code == 200
    assert "No recipients found" in res.text
    assert EventSimulation.objects.get().status == Occurrence.Status.PROCESSING.value


def test_debug_event_sync_failure(app: "DjangoTestApp", debug_context: "Context") -> None:
    from unittest.mock import patch

    from bitcaster.models import EventSimulation, Occurrence

    event: "Event" = debug_context["event"]
    opts: "Options[Event]" = event._meta
    url = reverse(admin_urlname(opts, "debug_event"), args=[event.pk])  # type: ignore[arg-type]
    with patch("bitcaster.admin.event.Occurrence.preview", side_effect=RuntimeError("boom")):
        res = app.post(url, {"context": "{}", "mode": "fast"}).follow()
    assert res.status_code == 200
    simulation = EventSimulation.objects.get()
    assert simulation.status == Occurrence.Status.FAILED.value
    assert simulation.data["errors"] == ["RuntimeError: boom"]
    assert "Simulation failed" in res.text
    assert 'http-equiv="refresh"' not in res.text


def test_debug_event_missing_template_ui(app: "DjangoTestApp", context: "Context") -> None:
    from testutils.factories import DeliverySimulationFactory, EventSimulationFactory

    from bitcaster.models import EventSimulation, Occurrence

    event: "Event" = context["event"]
    notification = event.notifications.first()
    channel = event.channels.first()
    sim: EventSimulation = EventSimulationFactory(
        event=event,
        created_by=app._user,
        mode="full",
        status=Occurrence.Status.PROCESSING,
        data={
            "delivered": [],
            "errors": [],
            "notifications": [notification.pk],
            "channels": [channel.pk],
            "messages": [],
            "recipients_count": 1,
            "rendered_count": 0,
            "missing_template_count": 1,
        },
    )
    DeliverySimulationFactory(
        simulation=sim,
        assignment=context["assignment"],
        notification=notification,
        message_template=None,
        status=Occurrence.Status.PROCESSING,
    )
    opts: "Options[Event]" = event._meta
    url = reverse(admin_urlname(opts, "debug_event"), args=[event.pk])  # type: ignore[arg-type]
    res = app.get(url, {"simulation": sim.pk})
    assert res.status_code == 200
    assert "Recipients without a message template were skipped" in res.text
    assert "missing" in res.text
    assert Occurrence.objects.count() == 0
    assert EventSimulation.objects.get().status == Occurrence.Status.PROCESSING.value


def test_debug_event_session_persists(app: "DjangoTestApp", debug_context: "Context") -> None:
    event: "Event" = debug_context["event"]
    opts: "Options[Event]" = event._meta
    url = reverse(admin_urlname(opts, "debug_event"), args=[event.pk])  # type: ignore[arg-type]
    app.post(url, {"context": '{"foo": "bar"}', "mode": "fast"})
    res = app.get(url)
    assert res.status_code == 200
    assert "{&quot;foo&quot;: &quot;bar&quot;}" in res.text  # context pre-filled from session


def test_debug_event_background_post(app: "DjangoTestApp", debug_context: "Context") -> None:
    from unittest.mock import patch

    from bitcaster.models import EventSimulation, Occurrence

    event: "Event" = debug_context["event"]
    opts: "Options[Event]" = event._meta
    url = reverse(admin_urlname(opts, "debug_event"), args=[event.pk])  # type: ignore[arg-type]
    with patch("bitcaster.admin.event.run_event_simulation.send") as mock_send:
        res = app.post(url, {"context": '{"foo": "bar"}', "mode": "full"})
    simulation = EventSimulation.objects.get()
    assert simulation.event == event
    assert simulation.status == Occurrence.Status.NEW.value
    assert simulation.mode == "full"
    assert simulation.context == {"foo": "bar"}
    mock_send.assert_called_once_with(simulation.pk)
    assert res.status_code == 302
    assert f"simulation={simulation.pk}" in res["Location"]


def test_debug_event_background_running(app: "DjangoTestApp", debug_context: "Context") -> None:
    from testutils.factories import EventSimulationFactory

    event: "Event" = debug_context["event"]
    sim = EventSimulationFactory(event=event, created_by=app._user, mode="full")
    opts: "Options[Event]" = event._meta
    url = reverse(admin_urlname(opts, "debug_event"), args=[event.pk])  # type: ignore[arg-type]
    res = app.get(url, {"simulation": sim.pk})
    assert res.status_code == 200
    assert 'http-equiv="refresh" content="3"' in res.text
    assert "Simulation running..." in res.text


def test_debug_event_background_processed(app: "DjangoTestApp", debug_context: "Context") -> None:
    from testutils.factories import EventSimulationFactory

    from bitcaster.models import EventSimulation, Occurrence

    event: "Event" = debug_context["event"]
    data = {
        "delivered": [],
        "recipients": [
            [
                debug_context["assignment"].address.value,
                debug_context["channel"].name,
                debug_context["assignment"].pk,
                debug_context["channel"].pk,
                event.notifications.first().pk,
                event.notifications.first().get_message(debug_context["channel"]).pk,
            ]
        ],
        "errors": [],
        "notifications": [event.notifications.first().pk],
        "channels": [debug_context["channel"].pk],
        "messages": [event.notifications.first().get_message(debug_context["channel"]).pk],
        "rendered": [
            {
                "assignment_pk": debug_context["assignment"].pk,
                "notification_pk": event.notifications.first().pk,
                "notification_name": event.notifications.first().name,
                "channel_pk": debug_context["channel"].pk,
                "channel_name": debug_context["channel"].name,
                "address": debug_context["assignment"].address.value,
                "subject": "",
                "message": "Hello bar",
                "html_message": "",
            }
        ],
        "missing_template": [],
    }
    sim: EventSimulation = EventSimulationFactory(
        event=event, created_by=app._user, mode="full", status=Occurrence.Status.PROCESSING, data=data
    )
    from testutils.factories import DeliverySimulationFactory

    notification = event.notifications.first()
    DeliverySimulationFactory(
        simulation=sim,
        assignment=debug_context["assignment"],
        notification=notification,
        message_template=notification.get_message(debug_context["channel"]),
        status=Occurrence.Status.PROCESSING,
        data={"rendered": {"subject": "", "message": "Hello bar", "html_message": ""}},
    )
    opts: "Options[Event]" = event._meta
    url = reverse(admin_urlname(opts, "debug_event"), args=[event.pk])  # type: ignore[arg-type]
    res = app.get(url, {"simulation": sim.pk})
    assert res.status_code == 200
    assert "Simulation completed" in res.text
    assert "Hello bar" in res.text
    assert 'http-equiv="refresh"' not in res.text


def test_debug_event_background_timeout(app: "DjangoTestApp", debug_context: "Context") -> None:
    from datetime import timedelta

    from freezegun import freeze_time
    from testutils.factories import EventSimulationFactory

    from django.utils import timezone

    from bitcaster.models import EventSimulation, Occurrence

    event: "Event" = debug_context["event"]
    sim: EventSimulation = EventSimulationFactory(event=event, created_by=app._user, mode="full")
    opts: "Options[Event]" = event._meta
    url = reverse(admin_urlname(opts, "debug_event"), args=[event.pk])  # type: ignore[arg-type]
    with freeze_time(timezone.now() + timedelta(minutes=11)):
        res = app.get(url, {"simulation": sim.pk})
    assert res.status_code == 200
    sim.refresh_from_db()
    assert sim.status == Occurrence.Status.FAILED.value
    assert sim.data["errors"] == ["simulation timed out"]
    assert "Simulation failed" in res.text
    assert 'http-equiv="refresh"' not in res.text


def test_debug_event_background_superseded(app: "DjangoTestApp", debug_context: "Context") -> None:
    event: "Event" = debug_context["event"]
    opts: "Options[Event]" = event._meta
    url = reverse(admin_urlname(opts, "debug_event"), args=[event.pk])  # type: ignore[arg-type]
    res = app.get(url, {"simulation": 9999})
    assert res.status_code == 200
    assert "superseded by a newer run" in res.text


def test_debug_event_simulation_wrong_event(app: "DjangoTestApp", debug_context: "Context") -> None:
    from testutils.factories import EventSimulationFactory

    event: "Event" = debug_context["event"]
    other = EventSimulationFactory(mode="full")
    opts: "Options[Event]" = event._meta
    url = reverse(admin_urlname(opts, "debug_event"), args=[event.pk])  # type: ignore[arg-type]
    res = app.get(url, {"simulation": other.pk}, expect_errors=True)
    assert res.status_code == 404


def test_debug_event_new_simulation_deletes_previous(app: "DjangoTestApp", debug_context: "Context") -> None:
    from testutils.factories import EventSimulationFactory
    from unittest.mock import patch

    from bitcaster.models import EventSimulation

    event: "Event" = debug_context["event"]
    old = EventSimulationFactory(event=event, created_by=app._user, mode="fast")
    opts: "Options[Event]" = event._meta
    url = reverse(admin_urlname(opts, "debug_event"), args=[event.pk])  # type: ignore[arg-type]
    with patch("bitcaster.admin.event.run_event_simulation.send"):
        res = app.post(url, {"context": "{}", "mode": "full"})
    assert res.status_code == 302
    assert not EventSimulation.objects.filter(pk=old.pk).exists()
    assert EventSimulation.objects.filter(event=event).count() == 1


def test_debug_event_prepopulate_from_simulation(app: "DjangoTestApp", debug_context: "Context") -> None:
    from testutils.factories import EventSimulationFactory

    event: "Event" = debug_context["event"]
    opts: "Options[Event]" = event._meta
    url = reverse(admin_urlname(opts, "debug_event"), args=[event.pk])  # type: ignore[arg-type]
    # a previous run leaves a session context, but the simulation params must win
    app.post(url, {"context": '{"foo": "from-session"}', "mode": "fast"})
    sim = EventSimulationFactory(
        event=event,
        created_by=app._user,
        mode="full",
        context={"foo": "from-simulation"},
        options={"limit_to": ["a@example.com"], "channels": [debug_context["channel"].pk]},
    )
    res = app.get(url, {"simulation": sim.pk})
    assert res.status_code == 200
    assert "from-simulation" in res.text  # simulation params beat session context


def test_debug_event_lossy_options_preserved_in_payload(app: "DjangoTestApp", debug_context: "Context") -> None:
    from testutils.factories import EventSimulationFactory

    event: "Event" = debug_context["event"]
    sim = EventSimulationFactory(event=event, created_by=app._user, mode="fast", options={"filters": {"include": []}})
    opts: "Options[Event]" = event._meta
    url = reverse(admin_urlname(opts, "debug_event"), args=[event.pk])  # type: ignore[arg-type]
    res = app.get(url, {"simulation": sim.pk})
    assert res.status_code == 200
    assert "&quot;include&quot;" in res.text  # filters carried into the emulation payload editor


def test_debug_event_invalid_limit_to_rejected(app: "DjangoTestApp", debug_context: "Context") -> None:
    from bitcaster.models import EventSimulation

    event: "Event" = debug_context["event"]
    opts: "Options[Event]" = event._meta
    url = reverse(admin_urlname(opts, "debug_event"), args=[event.pk])  # type: ignore[arg-type]
    res = app.post(url, {"context": "{}", "mode": "fast", "limit_to": "ghost@example.com"})
    assert res.status_code == 200
    assert "Unknown address(es)" in res.text
    assert EventSimulation.objects.count() == 0


def test_debug_event_invalid_simulation_param_is_stale(app: "DjangoTestApp", debug_context: "Context") -> None:
    event: "Event" = debug_context["event"]
    opts: "Options[Event]" = event._meta
    url = reverse(admin_urlname(opts, "debug_event"), args=[event.pk])  # type: ignore[arg-type]
    res = app.get(url, {"simulation": "not-an-int"})
    assert res.status_code == 200
    assert "superseded by a newer run" in res.text


def test_debug_event_all_channels_selected_by_default(app: "DjangoTestApp", debug_context: "Context") -> None:
    from testutils.factories import ChannelFactory

    event: "Event" = debug_context["event"]
    extra = ChannelFactory()
    event.channels.add(extra)
    opts: "Options[Event]" = event._meta
    url = reverse(admin_urlname(opts, "debug_event"), args=[event.pk])  # type: ignore[arg-type]
    res = app.get(url)
    assert res.status_code == 200
    assert "Simulation completed" not in res.text
    form = res.forms["debug-form"]
    options = form.get("channels").options
    assert len(options) == 2
    assert all(opt[1] for opt in options)


def test_debug_event_post_with_channels(app: "DjangoTestApp", debug_context: "Context") -> None:
    from bitcaster.models import EventSimulation, Occurrence

    event: "Event" = debug_context["event"]
    channel = debug_context["channel"]
    opts: "Options[Event]" = event._meta
    url = reverse(admin_urlname(opts, "debug_event"), args=[event.pk])  # type: ignore[arg-type]
    res = app.post(
        url,
        {"context": '{"foo": "bar"}', "mode": "fast", "channels": [str(channel.pk)]},
    ).follow()
    assert res.status_code == 200
    assert "Enter a list of values." not in res.text
    simulation = EventSimulation.objects.get()
    assert simulation.options["channels"] == [channel.pk]
    assert simulation.status == Occurrence.Status.PROCESSING.value


def test_debug_event_emulates_api_call(app: "DjangoTestApp", debug_context: "Context") -> None:
    from bitcaster.models import EventSimulation, Occurrence

    event: "Event" = debug_context["event"]
    channel = debug_context["channel"]
    opts: "Options[Event]" = event._meta
    url = reverse(admin_urlname(opts, "debug_event"), args=[event.pk])  # type: ignore[arg-type]
    payload = '{"payload_context": {"foo": "bar"}, "options": {"channels": ["%s"]}}' % channel.pk
    res = app.post(url, {"mode": "fast", "api_payload": payload}).follow()
    assert res.status_code == 200
    simulation = EventSimulation.objects.get()
    assert simulation.context == {"foo": "bar"}
    assert simulation.options["channels"] == [channel.pk]
    assert simulation.status == Occurrence.Status.PROCESSING.value


def test_debug_event_emulate_api_rejects_disabled_channel(app: "DjangoTestApp", debug_context: "Context") -> None:
    from testutils.factories import ChannelFactory

    from bitcaster.models import EventSimulation

    event: "Event" = debug_context["event"]
    other = ChannelFactory(active=False)
    opts: "Options[Event]" = event._meta
    url = reverse(admin_urlname(opts, "debug_event"), args=[event.pk])  # type: ignore[arg-type]
    payload = '{"options": {"channels": ["%s"]}}' % other.pk
    res = app.post(url, {"mode": "fast", "api_payload": payload})
    assert res.status_code == 200
    assert "not enabled for this event" in res.text
    assert EventSimulation.objects.count() == 0


def test_debug_event_channels_queryset(app: "DjangoTestApp", debug_context: "Context") -> None:
    from testutils.factories import ChannelFactory

    event: "Event" = debug_context["event"]
    other_channel = ChannelFactory()
    opts: "Options[Event]" = event._meta
    url = reverse(admin_urlname(opts, "debug_event"), args=[event.pk])  # type: ignore[arg-type]
    res = app.get(url)
    assert res.status_code == 200
    options = list(res.pyquery("#id_channels option"))
    pks = {int(opt.attrib["value"]) for opt in options}
    assert debug_context["channel"].pk in pks
    assert other_channel.pk not in pks


def test_debug_event_changelist_badge(app: "DjangoTestApp", debug_context: "Context") -> None:
    from testutils.factories import EventSimulationFactory

    from bitcaster.models import EventSimulation, Occurrence

    event: "Event" = debug_context["event"]
    url = reverse("admin:bitcaster_event_changelist")  # type: ignore[arg-type]
    res = app.get(url)
    assert "simulation running" not in res.text
    EventSimulationFactory(event=event, created_by=app._user, mode="full")
    res = app.get(url)
    assert "simulation running" in res.text
    EventSimulation.objects.update(status=Occurrence.Status.PROCESSING)
    res = app.get(url)
    assert "simulation running" not in res.text


def test_trigger_instructions(app: "DjangoTestApp", event: "Event") -> None:
    from testutils.factories import ApiKeyFactory

    ApiKeyFactory(
        application=event.application,
        project=event.application.project,
        organization=event.application.project.organization,
        name="Test Api Key",
    )
    opts: "Options[Event]" = event._meta
    url = reverse(admin_urlname(opts, "trigger_instructions"), args=[event.pk])  # type: ignore[arg-type]
    res = app.get(url)
    assert res.status_code == 200
    assert event.get_trigger_url() in res.text
    assert "Available API Keys" in res.text
    assert "Test Api Key" in res.text


def test_trigger_instructions_no_apikey_permission(app: "DjangoTestApp", event: "Event") -> None:
    from testutils.factories import ApiKeyFactory
    from testutils.perms import user_grant_permissions

    ApiKeyFactory(
        application=event.application,
        project=event.application.project,
        organization=event.application.project.organization,
        name="Test Api Key",
    )
    app._user.is_superuser = False
    app._user.save()
    opts: "Options[Event]" = event._meta
    url = reverse(admin_urlname(opts, "trigger_instructions"), args=[event.pk])  # type: ignore[arg-type]
    with user_grant_permissions(app._user, permissions=["bitcaster.view_event"]):
        res = app.get(url)
    assert res.status_code == 200
    assert "Available API Keys" not in res.text
    assert "Test Api Key" not in res.text
