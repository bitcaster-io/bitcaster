# -*- coding: utf-8 -*-
from django.contrib.admin import AdminSite


class MercuryAdminSite(AdminSite):
    def __init__(self, name='admin2'):
        super().__init__(name)


site = MercuryAdminSite()
