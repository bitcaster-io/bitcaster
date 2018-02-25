# -*- coding: utf-8 -*-
from django.contrib.admin import AdminSite
from django.utils.translation import gettext_lazy


class MercuryAdminSite(AdminSite):
    site_title = "Bitcaster"
    site_header = gettext_lazy('Django administration')
    index_title = gettext_lazy('Site administration')

    def __init__(self, name='admin2'):
        super().__init__(name)


site = MercuryAdminSite()
