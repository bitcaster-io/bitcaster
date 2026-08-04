from typing import TYPE_CHECKING, TypedDict

import pytest
from testutils.factories import EventSimulationFactory

from django.urls import reverse
from django_webtest import DjangoTestApp
from django_webtest.pytest_plugin import MixinWithInstanceVariables

from bitcaster.models import EventSimulation

if TYPE_CHECKING:
    from bitcaster.models import User

    Context = TypedDict(
        "Context",
        {
            "simulation": EventSimulation,
        },
    )


@pytest.fixture
def app(django_app_factory: MixinWithInstanceVariables, admin_user: "User") -> DjangoTestApp:
    django_app: DjangoTestApp = django_app_factory(csrf_checks=False)
    django_app.set_user(admin_user)
    django_app._user = admin_user
    return django_app


@pytest.fixture
def context(admin_user: "User") -> "Context":
    sim = EventSimulationFactory(created_by=admin_user, mode="full")
    return {"simulation": sim}


def test_changelist_shows_simulations(app: DjangoTestApp, context: "Context") -> None:
    url = reverse("admin:bitcaster_eventsimulation_changelist")
    res = app.get(url)
    assert res.status_code == 200
    assert str(context["simulation"].pk) in res.text


def test_no_add_permission(app: DjangoTestApp) -> None:
    res = app.get(reverse("admin:bitcaster_eventsimulation_add"), expect_errors=True)
    assert res.status_code == 403


def test_no_change_permission_on_post(app: DjangoTestApp, context: "Context") -> None:
    url = reverse("admin:bitcaster_eventsimulation_change", args=[context["simulation"].pk])
    res = app.post(url, {"name": "x"}, expect_errors=True)
    assert res.status_code == 403


def test_detail_shows_trigger_payload(app: DjangoTestApp, context: "Context") -> None:
    from bitcaster.models import Occurrence

    sim = context["simulation"]
    sim.context = {"foo": "bar"}
    sim.options = {"limit_to": ["a@example.com"]}
    sim.status = Occurrence.Status.PROCESSING.value
    sim.save()

    url = reverse("admin:bitcaster_eventsimulation_change", args=[sim.pk])
    res = app.get(url)
    assert res.status_code == 200
    assert "How the simulation was triggered" in res.text
    payload = res.pyquery("pre").text()
    assert "payload_context" in payload
    assert '"foo": "bar"' in payload
    assert "a@example.com" in payload


def test_detail_shows_curl_command(app: DjangoTestApp, context: "Context") -> None:
    from bitcaster.models import Occurrence

    sim = context["simulation"]
    sim.context = {"foo": "bar"}
    sim.options = {"limit_to": ["a@example.com"]}
    sim.status = Occurrence.Status.PROCESSING.value
    sim.save()
    event = sim.event

    url = reverse("admin:bitcaster_eventsimulation_change", args=[sim.pk])
    res = app.get(url)
    assert res.status_code == 200
    assert "Invoke the same call with curl" in res.text
    trigger_tab = res.pyquery(".fieldset-trigger")
    assert len(trigger_tab) == 1
    assert "dark:bg-base-900" in trigger_tab.eq(0).attr("class") or "dark:bg-base-900" in trigger_tab.html()
    assert "dark:border-base-800" in trigger_tab.html()
    curl = trigger_tab.find("pre").eq(1).text()
    assert "curl -X POST" in curl
    result_tab = res.pyquery(".fieldset-result")
    assert len(result_tab) == 1
    assert "curl -X POST" not in result_tab.text()
    trigger_url = reverse(
        "api:event-trigger",
        args=[
            event.application.project.organization.slug,
            event.application.project.slug,
            event.application.slug,
            event.slug,
        ],
    )
    assert f"https://<HOST>{trigger_url}" in curl
    assert "Authorization: Key <API_KEY>" in curl
    assert "curl -X POST" in curl
    assert "payload_context" in curl
    assert "limit_to" in curl


def test_detail_links_to_delivery_simulations(app: DjangoTestApp, context: "Context") -> None:
    url = reverse("admin:bitcaster_eventsimulation_change", args=[context["simulation"].pk])
    res = app.get(url)
    assert res.status_code == 200
    changelist = reverse("admin:bitcaster_deliverysimulation_changelist")
    assert f'href="{changelist}?simulation__exact={context["simulation"].pk}"' in res.text
    assert "Delivery simulations" in res.text


def test_view_deliveries_hidden_without_original() -> None:
    from unittest.mock import Mock

    from bitcaster.admin.eventsimulation import EventSimulationAdmin

    admin = EventSimulationAdmin(EventSimulation, Mock())
    button = Mock()
    button.context = {"original": None}
    admin.view_deliveries.func(admin, button)
    button.href = None
    assert button.visible is False


def test_delete_allowed(app: DjangoTestApp, context: "Context") -> None:
    url = reverse("admin:bitcaster_eventsimulation_delete", args=[context["simulation"].pk])
    res = app.get(url)
    assert res.status_code == 200
    form = res.forms[2]
    form.submit().follow()
    assert not EventSimulation.objects.filter(pk=context["simulation"].pk).exists()


def test_purge_button(app: DjangoTestApp, monkeypatch: pytest.MonkeyPatch) -> None:
    from unittest.mock import Mock

    monkeypatch.setattr("bitcaster.admin.eventsimulation.purge_event_simulations.send", purge_mock := Mock())

    url_redirect = reverse("admin:bitcaster_eventsimulation_changelist")
    url = reverse("admin:bitcaster_eventsimulation_purge")
    res = app.get(url, headers={"REFERER": url_redirect})
    assert res.status_code == 200
    assert "Purge event simulations" in res.text

    res = res.forms["confirm-form"].submit()
    assert res.location == url_redirect
    res = res.follow()
    assert "Event simulations purge has been successfully triggered" in res.text
    purge_mock.assert_called_once()


def test_deliveries_page(app: DjangoTestApp) -> None:
    from testutils.factories import (
        AssignmentFactory,
        ChannelFactory,
        DeliverySimulationFactory,
        EventSimulationFactory,
        MessageTemplateFactory,
        NotificationFactory,
    )

    from bitcaster.models import Occurrence

    sim = EventSimulationFactory(status=Occurrence.Status.PROCESSING.value, mode="full")
    channel = ChannelFactory()
    asm = AssignmentFactory(channel=channel)
    notification = NotificationFactory(event=sim.event, distribution__recipients=[asm])
    msg = MessageTemplateFactory(
        channel=channel, event=sim.event, notification=notification, content="Hello {{ event.name }}"
    )
    DeliverySimulationFactory(
        simulation=sim,
        assignment=asm,
        notification=notification,
        message_template=msg,
        status=Occurrence.Status.PROCESSING,
        data={"rendered": {"subject": "Hi", "message": "Hello", "html_message": ""}},
    )

    url = reverse("admin:bitcaster_eventsimulation_deliveries", args=[sim.pk])
    res = app.get(url)
    assert res.status_code == 200
    assert asm.address.value in res.text
    assert "Hello" in res.text


def test_deliveries_page_pagination(app: DjangoTestApp) -> None:
    from constance.test.pytest import override_config

    from testutils.factories import (
        AssignmentFactory,
        ChannelFactory,
        DeliverySimulationFactory,
        EventSimulationFactory,
        NotificationFactory,
    )

    from bitcaster.models import Occurrence

    sim = EventSimulationFactory(status=Occurrence.Status.PROCESSING.value, mode="partial")
    channel = ChannelFactory()
    notification = NotificationFactory(event=sim.event, distribution__recipients=[])
    for i in range(3):
        asm = AssignmentFactory(channel=channel, address__value=f"user{i}@example.com")
        notification.distribution.recipients.add(asm)
        DeliverySimulationFactory(
            simulation=sim,
            assignment=asm,
            notification=notification,
            status=Occurrence.Status.PROCESSING.value,
            data={"rendered": {"subject": "", "message": f"Hello {i}", "html_message": ""}},
        )

    url = reverse("admin:bitcaster_eventsimulation_deliveries", args=[sim.pk])
    with override_config(EVENT_SIMULATION_PAGE_SIZE=2):
        res = app.get(url)
    assert res.status_code == 200
    assert "Page 1 of 2" in res.text
    assert "user0@example.com" in res.text
    assert "user2@example.com" not in res.text


def test_deliveries_page_denied_without_permission(app: DjangoTestApp) -> None:
    from testutils.factories import EventSimulationFactory, UserFactory

    sim = EventSimulationFactory(status="PROCESSED")
    user = UserFactory(username="limited", is_staff=True, is_superuser=False)
    app.set_user(user)

    url = reverse("admin:bitcaster_eventsimulation_deliveries", args=[sim.pk])
    res = app.get(url, expect_errors=True)
    assert res.status_code == 403


def test_deliverysimulation_changelist_forbidden(app: DjangoTestApp) -> None:
    from testutils.factories import EventSimulationFactory, UserFactory

    EventSimulationFactory()
    user = UserFactory(username="limited2", is_staff=True, is_superuser=False)
    app.set_user(user)

    url = reverse("admin:bitcaster_deliverysimulation_changelist")
    res = app.get(url, expect_errors=True)
    assert res.status_code == 403


def test_deliverysimulation_changelist_allowed(app: DjangoTestApp) -> None:
    from testutils.factories import (
        AssignmentFactory,
        ChannelFactory,
        DeliverySimulationFactory,
        EventSimulationFactory,
        NotificationFactory,
    )

    from bitcaster.models import Occurrence

    sim = EventSimulationFactory(status=Occurrence.Status.PROCESSING.value, mode="full")
    channel = ChannelFactory()
    asm = AssignmentFactory(channel=channel)
    notification = NotificationFactory(event=sim.event, distribution__recipients=[asm])
    DeliverySimulationFactory(simulation=sim, assignment=asm, notification=notification)

    url = reverse("admin:bitcaster_deliverysimulation_changelist")
    res = app.get(url)
    assert res.status_code == 200
    assert "Delivery simulations" in res.text
    assert str(sim) in res.text
