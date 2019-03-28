# -*- coding: utf-8 -*-
import logging

from django import forms

from bitcaster.models import Application, Team
from bitcaster.security import Role

logger = logging.getLogger(__name__)


class ApplicationCreateForm(forms.ModelForm):
    # slug = forms.SlugField(validators=[ReservedWordValidator()], required=False)

    class Meta:
        model = Application
        fields = ['name', 'timezone', ]

    def save(self, commit=True):
        obj = super().save(commit)
        Team.objects.create(application=obj, manager=obj.owner, name='Admins', role=Role.OWNER)
        Team.objects.create(application=obj, manager=obj.owner, name='Managers', role=Role.ADMIN)
        Team.objects.create(application=obj, manager=obj.owner, name='Subscribers', role=Role.SUBSCRIBER)

        return obj


class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['name', 'timezone', 'enabled']
