import pytest
from django.urls import reverse
from rest_framework import serializers
from strategy_field.utils import fqn
from webtest import Text, Select
from webtest.forms import MultipleSelect

pytestmark = pytest.mark.django_db


def add_argument(form):
    total_forms_field_name = 'form-TOTAL_FORMS'
    idx = int(form[total_forms_field_name].value)
    pos = idx + 2
    field = Text(form, 'input', name=f"form-{idx}-name",
                 pos=pos + 1, value=None)
    form.fields[f"form-{idx}-name"] = [field]
    form.field_order.append((f"form-{idx}-name", field))
    # form[f"form-{idx}-name"] = name

    field = Text(form, 'input', name=f"form-{idx}-type",
                 pos=pos + 1, value=None)
    form.fields[f"form-{idx}-type"] = [field]
    form.field_order.append((f"form-{idx}-type", field))
    # form[f"form-{idx}-type"] = _type

    form[total_forms_field_name] = idx + 1
    return idx

def add_message(form, application):
    total_forms_field_name = 'b-TOTAL_FORMS'
    idx = int(form[total_forms_field_name].value)
    pos = idx + 2

    field = MultipleSelect(form, 'select', name=f"b-{idx}-channels",
                           pos=pos + 1, value=None)
    field.options = [(str(a), False, c) for a, c in application.channels.values_list('id',
                                                                                     'name')]
    form.fields[f"b-{idx}-channels"] = [field]
    form.field_order.append((f"b-{idx}-channels", field))

    field = Text(form, 'input', name=f"b-{idx}-subject",
                 pos=pos + 1, value=None)
    form.fields[f"b-{idx}-subject"] = [field]
    form.field_order.append((f"b-{idx}-subject", field))

    field = Text(form, 'input', name=f"b-{idx}-body",
                 pos=pos + 1, value=None)
    form.fields[f"b-{idx}-body"] = [field]
    form.field_order.append((f"b-{idx}-body", field))

    field = Select(form, 'select', name=f"b-{idx}-language",
                   pos=pos + 1, value=None)
    field.options = [('all', False, 'All')]
    form.fields[f"b-{idx}-language"] = [field]
    form.field_order.append((f"b-{idx}-language", field))

    form[total_forms_field_name] = idx + 1
    return idx


def test_create_event(django_app, channel1):
    application = channel1.application
    organization = application.organization
    owner = organization.owner
    url = reverse('app-event-list', args=[organization.slug,
                                          application.slug])
    res = django_app.get(url, user=owner.email)
    res = res.click("Create Event")
    res.form['a-name'] = 'Event1'
    idx = add_argument(res.form)
    res.form[f'form-{idx}-name'] = "field22"
    res.form[f'form-{idx}-type'] = fqn(serializers.CharField)

    res = res.form.submit()
    idx = add_message(res.form, application)
    res.form[f'b-{idx}-channels'].select_multiple([str(channel1.pk)])
    res.form[f'b-{idx}-subject'] = 'subject'
    res.form[f'b-{idx}-body'] = 'body'
    res.form[f'b-{idx}-language'] = 'all'

    res = res.form.submit().follow()
    event = application.events.first()
    assert event
    assert event.arguments == {"fields": [{"name": "field22",
                                           "type": fqn(serializers.CharField)}]}

    message = event.messages.first()
    assert list(message.channels.all()) == [channel1]
    assert message.subject == 'subject'
    assert message.body == 'body'


def test_update_event(django_app, message1):
    event = message1.event
    application = event.application
    organization = application.organization
    owner = organization.owner
    url = reverse('app-event-update', args=[organization.slug,
                                            application.slug,
                                            event.pk])
    res = django_app.get(url, user=owner.email)
    res.form['a-name'] = 'Event-updated'
    idx = add_argument(res.form)
    res.form[f'form-{idx}-name'] = "field-added"
    res.form[f'form-{idx}-type'] = fqn(serializers.CharField)

    res = res.form.submit()
    res.form[f'b-0-subject'] = 'subject-updated'
    res.form[f'b-0-body'] = 'body-updated'
    res = res.form.submit().follow()

    event.refresh_from_db()
    assert event.arguments == {"fields": [{"name": "field-added",
                                           "type": fqn(serializers.CharField)}]}

    message = event.messages.first()
    # assert list(message.channels.all()) == [channel1]
    assert message.subject == 'subject-updated'
    assert message.body == 'body-updated'
