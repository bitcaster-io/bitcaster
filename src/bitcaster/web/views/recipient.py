# -*- coding: utf-8 -*-
"""
bitcaster / recipient
~~~~~~~~~~~~~~~~~

:copyright: (c) 2018 Stefano Apostolico, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""
from bitcaster.web.views import BitcasterTemplateView


class RecipientHome(BitcasterTemplateView):
    template_name = 'bitcaster/recipient/home.html'
