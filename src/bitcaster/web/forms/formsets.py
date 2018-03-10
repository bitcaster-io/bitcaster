# -*- coding: utf-8 -*-
"""
mercury / formsets
~~~~~~~~~~~~~~~~~

:copyright: (c) 2018 Stefano Apostolico, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

import logging

from django import forms

from bitcaster.models import Organization, OrganizationMember

logger = logging.getLogger(__name__)


class OrganizationInvitationForm(forms.ModelForm):
    email = forms.EmailField(required=True,
                             widget=forms.EmailInput(attrs={'autocomplete': 'email'}))

    class Meta:
        model = OrganizationMember
        fields = ('email', 'role')


OrganizationInvitationFormSet = forms.inlineformset_factory(Organization,
                                                            OrganizationMember,
                                                            form=OrganizationInvitationForm,
                                                            min_num=1,
                                                            extra=0)
