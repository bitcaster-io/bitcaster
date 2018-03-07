# -*- coding: utf-8 -*-
"""
mercury / recipient
~~~~~~~~~~~~~~~~~

:copyright: (c) 2018 Stefano Apostolico, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""
from mercury.web.views import MercuryTemplateView


class RecipientHome(MercuryTemplateView):
    template_name = 'bitcaster/recipient/home.html'
