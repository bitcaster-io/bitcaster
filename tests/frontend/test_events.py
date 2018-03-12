import pytest
from django.urls import reverse
from rest_framework import serializers
from strategy_field.utils import fqn
from webtest import Text

pytestmark = pytest.mark.django_db


def add_argument(form, name, _type):
    total_forms_field_name = 'form-TOTAL_FORMS'
    idx = int(form[total_forms_field_name].value)
    pos = idx + 2
    field = Text(form, 'input', name=f"form-{idx}-name",
                 pos=pos + 1, value=name)
    form.fields[f"form-{idx}-name"] = [field]
    form.field_order.append((f"form-{idx}-name", field))
    form[f"form-{idx}-name"] = name

    field = Text(form, 'input', name=f"form-{idx}-type",
                 pos=pos + 1, value=_type)
    form.fields[f"form-{idx}-type"] = [field]
    form.field_order.append((f"form-{idx}-type", field))
    form[f"form-{idx}-type"] = _type

    form[total_forms_field_name] = idx + 1


def test_create_event(django_app, application1):
    organization = application1.organization
    owner = organization.owner
    url = reverse('app-event-list', args=[organization.slug,
                                          application1.slug])
    res = django_app.get(url, user=owner.email)
    res = res.click("Create Event")
    res.form['name'] = 'Event1'
    add_argument(res.form, "field22", fqn(serializers.CharField))
    res.form.submit().follow()

    event = application1.events.first()
    assert event
    assert event.arguments == {"fields": [{"name": "field22",
                                           "type": fqn(serializers.CharField)}]}


def test_update_event(django_app, event1):
    application = event1.application
    organization = application.organization
    owner = organization.owner
    url = reverse('app-event-update', args=[organization.slug,
                                            application.slug,
                                            event1.pk])
    res = django_app.get(url, user=owner.email)
    res.form['name'] = 'Event12'
    add_argument(res.form, "field_updated", fqn(serializers.CharField))
    res.form.submit().follow()

    event = application.events.first()
    assert event
    assert event.arguments == {"fields": [{"name": "field_updated",
                                           "type": fqn(serializers.CharField)}]}
