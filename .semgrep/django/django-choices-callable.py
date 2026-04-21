from django.db import models
from django.forms import forms


def get_choices():
    return [("a", "A")]


class Status(models.TextChoices):
    OK = "ok", "OK"


MY_CHOICES = [("1", "One")]


class MyModel(models.Model):
    # ok: django-choices-must-be-callable
    valid_field = models.CharField(max_length=10, choices=get_choices)

    # ok: django-choices-must-be-callable
    another_valid = models.CharField(choices=Status.choices)

    # ruleid: django-choices-must-be-callable
    invalid_literal_list = models.CharField(choices=[("a", "A")])

    # ruleid: django-choices-must-be-callable
    invalid_literal_tuple = models.CharField(choices=(("a", "A"),))

    # ruleid: django-choices-must-be-callable
    invalid_constant = models.CharField(choices=MY_CHOICES)


class MyForm(forms.Form):
    # ok: django-choices-must-be-callable
    field1 = forms.ChoiceField(choices=get_choices)

    # ruleid: django-choices-must-be-callable
    field2 = forms.ChoiceField(choices=[(1, 1)])
