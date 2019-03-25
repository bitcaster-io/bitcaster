# -*- coding: utf-8 -*-
import logging

from django.utils.translation import gettext_lazy as _

from bitcaster.models import Application
from bitcaster.web.forms import AddressForm

from ..base import BitcasterBaseListView
from .base import UserMixin

logger = logging.getLogger(__name__)

__all__ = ('UserApplicationListView', )


class UserApplicationListView(UserMixin, BitcasterBaseListView):
    template_name = 'bitcaster/user/application_list.html'
    model = Application
    form_class = AddressForm
    title = _('Applications')

    def get_queryset(self):
        return Application.objects.filter(teams__members__user=self.request.user)
