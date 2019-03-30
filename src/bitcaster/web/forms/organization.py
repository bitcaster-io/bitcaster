# -*- coding: utf-8 -*-
import logging

from django import forms

from bitcaster.models import Organization, OrganizationGroup
from bitcaster.web.forms.fields import EmailField

logger = logging.getLogger(__name__)


class OrganizationSystemForm(forms.ModelForm):
    class Meta:
        model = Organization
        fields = ('name', 'admin_email', 'slug', 'avatar',
                  'default_role', 'rate_limit')


class OrganizationGroupForm(forms.ModelForm):
    class Meta:
        model = OrganizationGroup
        fields = ('name', 'members')

    def __init__(self, organization, *args, **kwargs):
        self.organization = organization
        super(OrganizationGroupForm, self).__init__(*args, **kwargs)
        if 'applications' in self.fields:
            self.fields['applications'].queryset = self.organization.applications.all()

    # def save(self, commit=True):
    #     self.instance.organization = self.organization
    #     return super().save(commit)
    #
    # def full_clean(self):
    #     super().full_clean()

    # def clean_name(self):
    #     value = self.cleaned_data['name']
    #     if self.instance.pk:
    #         qs = self.organization.groups.filter(name=value).exclude(id=self.instance.pk)
    #     else:
    #         qs = self.organization.groups.filter(name=value)
    #
    #     if qs.exists():
    #         raise ValidationError('Group with this name already exists.')
    #     return value


class OrganizationForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'autocomplete': 'organization'}))
    admin_email = EmailField()

    class Meta:
        model = Organization
        fields = ('name', 'admin_email', 'slug')

    def __init__(self, *args, **kwargs):
        super(OrganizationForm, self).__init__(*args, **kwargs)
        if not self.instance or self.instance.is_core:
            self.fields['slug'].disabled = True
            self.fields['slug'].validators = []

    def clean_slug(self):
        value = self.cleaned_data['slug']
        if self.instance and self.instance.is_core:
            return self.instance.slug
        return value
