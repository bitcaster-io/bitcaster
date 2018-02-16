# -*- coding: utf-8 -*-
from django.contrib.admin import ModelAdmin, register, TabularInline
from django.contrib.admin.utils import unquote
from django.urls import reverse

from geo.forms import (administrativeareaform_factory_for_country,
                       AreaForm, CountryForm, LocationForm)
from geo.models import (AdministrativeArea, AdministrativeAreaType, Country,
                        CountryNameTranslation, Currency, Location, LocationType, )
from geo.templatetags.geo import flag


def tabular_factory(model, fields=None, inline=None, form=None, **kwargs):
    """ factory for TabularInline
    """
    attrs = {'model': model, 'fields': fields}
    read_only = kwargs.pop('read_only', False)
    if read_only:
        attrs['readonly_fields'] = fields
        attrs['can_delete'] = False

    Inline = inline or TabularInline
    name = "%sInLine" % model.__class__.__name__
    if form:
        attrs['form'] = form
    attrs.update(kwargs)
    Tab = type(str(name), (Inline,), attrs)
    return Tab


class SecurityMixin(object):
    readonly_fields = ('last_modified_date',)


@register(Currency)
class ICurrency(SecurityMixin, ModelAdmin):
    search_fields = ('name', 'iso_code')
    list_display = ('name', 'iso_code', 'symbol', 'used_by')
    inlines = [tabular_factory(Country, fields=['name'], read_only=True)]
    change_form_template = None

    def used_by(self, o):
        return ', '.join(['<a href="%s">%s</>' % (reverse('admin:geo_country_change', args=[c.pk]), c.name) for c in
                          Country.objects.filter(currency=o)])

    used_by.allow_tags = True


class AdministrativeAreaInline(TabularInline):
    model = AdministrativeArea
    exclude = ('capi_id',)
    raw_id_fields = ('parent', 'type')

    def get_formset(self, request, obj=None, **kwargs):
        self.form = administrativeareaform_factory_for_country(obj)
        return super(AdministrativeAreaInline, self).get_formset(request, obj, **kwargs)


@register(Country)
class CountryAdmin(SecurityMixin, ModelAdmin):
    form = CountryForm
    search_fields = ('name', 'undp', 'iso_code', 'iso_code3', 'iso_num',)
    list_display = ('name', 'continent', 'undp', 'iso_code', 'iso_code3', 'iso_num', 'currency', 'timezone', 'flag')
    list_filter = ('continent', 'region',)
    cell_filter = ('continent', 'region', 'currency')
    fieldsets = [(None, {'fields': (('name', 'fullname'),
                                    ('iso_code', 'iso_code3', 'iso_num'),
                                    ('undp', 'nato3',),
                                    ('itu', 'icao', 'fips'),
                                    ('region', 'continent', 'currency'),
                                    ('timezone', 'tld', 'phone_prefix'))})]
    inlines = (AdministrativeAreaInline,
               tabular_factory(AdministrativeAreaType, fields=('name', 'country', 'parent'), raw_id_fields=('parent',)))
    raw_id_fields = ('currency',)
    autocomplete_lookup_fields = {
        'fk': raw_id_fields
    }
    change_form_template = None

    def flag(self, o):
        return flag(o)

    flag.allow_tags = True

    def change_view(self, request, object_id, form_url='', extra_context=None):
        obj = self.get_object(request, unquote(object_id))
        context = {'nodes': obj.areas.all()}
        context.update(extra_context or {})
        return super(CountryAdmin, self).change_view(request, object_id, form_url, context)


@register(CountryNameTranslation)
class ICountryNameTranslation(SecurityMixin, ModelAdmin):
    search_fields = ('country__name',)
    list_display = ('country', 'language_iso_code', 'translation',)
    exclude = ('capi_id',)
    list_filter = ('country',)
    raw_id_fields = ('country',)
    autocomplete_lookup_fields = {
        'fk': raw_id_fields
    }


@register(Location)
class ILocation(SecurityMixin, ModelAdmin):
    search_fields = ('name',)
    form = LocationForm
    list_display = ('name', 'loccode', 'country', 'area', 'is_administrative', 'is_capital', 'lat', 'lng')
    list_display_rel_links = cell_filter = ('country', 'area', 'is_administrative', 'is_capital')
    list_filter = ('is_administrative', 'is_capital', 'country')
    raw_id_fields = ('country', 'area', 'type')
    autocomplete_lookup_fields = {
        'fk': raw_id_fields
    }


@register(AdministrativeArea)
class IArea(SecurityMixin, ModelAdmin):
    form = AreaForm
    search_fields = ('name',)
    list_display = ('name', 'parent', 'country', 'type', 'code')
    list_filter = ('type', 'country')
    inlines = (tabular_factory(Location, form=LocationForm, raw_id_fields=('country', 'area', 'type')),)
    raw_id_fields = ('country', 'parent', 'type')
    autocomplete_lookup_fields = {
        'fk': raw_id_fields
    }

    def change_view(self, request, object_id, form_url='', extra_context=None):
        obj = self.get_object(request, unquote(object_id))
        context = {'nodes': obj.areas.all()}
        context.update(extra_context or {})
        return super(IArea, self).change_view(request, object_id, form_url, context)


@register(LocationType)
class ILocationTypeAdmin(SecurityMixin, ModelAdmin):
    search_fields = ('description',)
    list_display = ('description',)


@register(AdministrativeAreaType)
class IAreaType(SecurityMixin, ModelAdmin):
    search_fields = ('name',)
    list_display = ('name', 'parent', 'country')
    list_display_rel_links = cell_filter = ('country',)
    list_filter = ('country',)
    inlines = (tabular_factory(AdministrativeArea, fields=('name', 'code', 'parent', 'country'),
                               raw_id_fields=('parent', 'country')),)
    raw_id_fields = ('country', 'parent')
    autocomplete_lookup_fields = {
        'fk': raw_id_fields
    }

    def change_view(self, request, object_id, form_url='', extra_context=None):
        obj = self.get_object(request, unquote(object_id))
        context = {'nodes': obj.children.all()}
        context.update(extra_context or {})
        return super(IAreaType, self).change_view(request, object_id, form_url, context)
