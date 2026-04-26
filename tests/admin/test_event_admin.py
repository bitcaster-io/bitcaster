from unittest.mock import patch

import pytest
from django.urls import reverse
from testutils.factories import AddressFactory, DistributionListFactory

from bitcaster.models import Event


@pytest.mark.django_db
def test_trigger_event_exception(django_app, superuser, event, assignment):
    # Setup: Ensure the assignment is linked to the superuser and a distribution list
    addr = AddressFactory(user=superuser)
    assignment.address = addr
    assignment.save()

    dl = DistributionListFactory(project=event.application.project)
    dl.recipients.add(assignment)

    url = reverse("admin:bitcaster_event_trigger_event", args=[event.pk])

    # Login as superuser
    django_app.set_user(superuser)

    # GET request to see if form is rendered correctly
    res = django_app.get(url)
    assert res.status_code == 200

    # Mock evt.trigger to raise an exception
    with patch.object(Event, "trigger", side_effect=Exception("Test Exception")):
        form = res.forms["test-form"]
        # select the assignment in the form.
        # assignment is a ModelChoiceField
        form["assignment"] = str(assignment.pk)
        res = form.submit()

    assert res.status_code == 200
    assert "Test Exception" in res.body.decode()


@pytest.mark.django_db
def test_trigger_event_success(django_app, superuser, event, assignment):
    # Setup: Ensure the assignment is linked to the superuser and a distribution list
    addr = AddressFactory(user=superuser)
    assignment.address = addr
    assignment.save()

    dl = DistributionListFactory(project=event.application.project)
    dl.recipients.add(assignment)

    url = reverse("admin:bitcaster_event_trigger_event", args=[event.pk])

    # Login as superuser
    django_app.set_user(superuser)

    # POST request
    res = django_app.get(url)
    form = res.forms["test-form"]
    form["assignment"] = str(assignment.pk)

    # Mock o.process and return a mock occurrence
    from unittest.mock import MagicMock

    with patch("bitcaster.models.Event.trigger") as mock_trigger:
        mock_occurrence = MagicMock()
        mock_occurrence.status = "OK"
        mock_occurrence.data = "Sent"
        mock_trigger.return_value = mock_occurrence

        res = form.submit().follow()

    assert res.status_code == 200
    assert "Sent OK - Sent" in res.body.decode()


@pytest.mark.django_db
def test_trigger_event_invalid_form(django_app, superuser, event, assignment):
    url = reverse("admin:bitcaster_event_trigger_event", args=[event.pk])
    django_app.set_user(superuser)
    res = django_app.get(url)
    form = res.forms["test-form"]
    # assignment is required, so leaving it empty makes the form invalid
    res = form.submit()
    assert res.status_code == 200
    assert "form" in res.context
    assert res.context["form"].errors
