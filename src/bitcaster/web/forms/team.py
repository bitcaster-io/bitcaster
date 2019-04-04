# -*- coding: utf-8 -*-
import logging

from django import forms

from bitcaster.models import ApplicationTeam

logger = logging.getLogger(__name__)


class ApplicationTeamAddMemberForm(forms.Form):
    user = forms.IntegerField()


class ApplicationCreateTeamForm(forms.ModelForm):
    pass


class ApplicationTeamForm(forms.ModelForm):
    class Meta:
        fields = ('name', 'manager')
        model = ApplicationTeam

    def __init__(self, application, *args, **kwargs):
        self.application = application
        super().__init__(*args, **kwargs)

        self.fields['manager'].queryset = self.application.members.all()
        # self.fields['manager'].widget.url = reverse('app-member-autocomplete',
        #                                             args=[self.application.organization.slug,
        #                                                   self.application.slug]
        #                                             )
