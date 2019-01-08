# -*- coding: utf-8 -*-
import logging

from django.db.models import F
from django.db.transaction import get_connection

logger = logging.getLogger(__name__)


class FF(F):
    _name = ''

    def __init__(self):
        super().__init__(self._name)


def toggler_factory(field_name):
    def toggle_activation(modeladmin, request, queryset):
        conn = get_connection()
        cursor = conn.cursor()
        tablename = modeladmin.model._meta.db_table
        update_status = f'UPDATE {tablename} SET {field_name} = (NOT {tablename}.{field_name})'
        cursor.execute(update_status)

    return toggle_activation


def activator_factory(field_name):
    def activate(modeladmin, request, queryset):
        queryset.update(**{field_name: True})

    return activate


def deactivator_factory(field_name):
    def deactivate(modeladmin, request, queryset):
        queryset.update(**{field_name: False})

    return deactivate
