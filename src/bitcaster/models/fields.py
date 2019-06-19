from django import forms
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models

from bitcaster.utils.ttl import encode_ttl, parse_ttl


class TTLFormField(forms.CharField):

    def prepare_value(self, value):
        return encode_ttl(value)

    def to_python(self, value):
        """Return a string."""
        if value not in self.empty_values:
            value = str(value)
            if self.strip:
                value = value.strip()
        if value in self.empty_values:
            return self.empty_value
        return parse_ttl(value)


DURATION = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}
IDURATION = {v: k for k, v in DURATION.items()}


class MinRateValidator(MinValueValidator):
    def get_rate_value(self, rate):
        num, period = rate.split('/')
        num_requests = int(num)
        return num_requests * DURATION[period[0]]

    def compare(self, a, b):
        return self.get_rate_value(a) < self.get_rate_value(b)


class ThrottleField(models.CharField):
    default_validators = [RegexValidator(r'(\d+)/(s|m|h|d|second|minute|hour|day)',
                                         message='Insert value in the form <num>/[second,minute,hour,day]')]

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('max_length', 10)
        self.min_value = kwargs.pop('min_value', '1/s')
        super().__init__(*args, **kwargs)

    def to_python(self, value):
        return self.parse_rate(value)

    def clean(self, value, model_instance):
        self.validate(value, model_instance)
        self.run_validators(value)
        return value

    def get_prep_value(self, value):
        value = super().get_prep_value(value)
        return '%s/%s' % (value[0], IDURATION[value[1]])

    def parse_rate(self, rate):
        """
        Given the request rate string, return a two tuple of:
        <allowed number of requests>, <period of time in seconds>
        """
        if rate is None:
            return (None, None)
        num, period = rate.split('/')
        num_requests = int(num)
        return (num_requests, DURATION[period[0]])


class TTLDBField(models.IntegerField):

    def __init__(self, *args, **kwargs):
        self.window = kwargs.pop('window', 1)
        super().__init__(*args, **kwargs)

    def clean(self, value, model_instance):
        value = super().clean(value, model_instance)
        return value // self.window

    def formfield(self, **kwargs):
        return super().formfield(**{
            'form_class': TTLFormField,
            **kwargs,
        })
