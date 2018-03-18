# -*- coding: utf-8 -*-
from bitcaster.web.views import BitcasterTemplateView


class RecipientHome(BitcasterTemplateView):
    template_name = 'bitcaster/recipient/home.html'
