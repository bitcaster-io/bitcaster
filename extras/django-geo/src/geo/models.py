# -*- coding: utf-8 -*-
import logging

from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.validators import MinLengthValidator, RegexValidator
from django.db import models
from django.db.models.manager import Manager
from django.utils.translation import ugettext_lazy as _
from mptt.managers import TreeManager
from mptt.models import MPTTModel, TreeForeignKey
from six import python_2_unicode_compatible
from timezone_field import TimeZoneField

logger = logging.getLogger('geo')

CONTINENTS = (
    ('AF', _('Africa')),
    ('AN', _('Antartica')),
    ('AS', _('Asia')),
    ('EU', _('Europe')),
    ('NA', _('North America')),
    ('OC', _('Oceania')),
    ('SA', _('South America')),
)


class LastUpdateDateModel(models.Model):
    last_modified_date = models.DateTimeField(auto_now=True,
                                              editable=False)

    class Meta:
        abstract = True


class CurrencyManager(Manager):
    use_for_related_fields = True

    def money(self, **kwargs):
        return self.exclude(iso_code__startswith='X', **kwargs)


@python_2_unicode_compatible
class Currency(LastUpdateDateModel):
    iso_code = models.CharField(max_length=5, db_index=True,
                                unique=True, help_text='ISO 4217 code')
    numeric_code = models.CharField(max_length=5, unique=True,
                                    help_text='ISO 4217 code')
    decimals = models.IntegerField(default=0)
    name = models.CharField(max_length=100)
    symbol = models.CharField(max_length=5, blank=True, null=True)

    objects = CurrencyManager()

    class Meta:
        app_label = 'geo'
        ordering = ['iso_code', ]
        verbose_name_plural = 'Currencies'

    def __str__(self):
        return '%s (%s)' % (self.iso_code, self.name)


@python_2_unicode_compatible
class UNRegion(LastUpdateDateModel):
    code = models.CharField(max_length=5, unique=True,
                            blank=False, null=False, db_index=True)

    name = models.CharField(max_length=100)

    class Meta:
        app_label = 'geo'
        verbose_name_plural = _('UN Regions')
        ordering = ['name']

    def __str__(self):
        return self.name


class CountryManager(Manager):
    use_for_related_fields = True

    def valid(self):
        return self.get_queryset().filter(expired__isnull=True)

    def _by_continent(self, continent):
        return self.valid().filter(continent=continent)

    def africa(self):
        return self._by_continent('AF')

    def asia(self):
        return self._by_continent('AS')

    def europe(self):
        return self._by_continent('EU')

    def north_america(self):
        return self._by_continent('NA')

    def south_america(self):
        return self._by_continent('SA')

    def oceania(self):
        return self._by_continent('OC')

    def antartica(self):
        return self._by_continent('AN')


REGIONS = {
    'OMD': 'West Africa',
    'OMJ': 'Southern Africa',
    'OMP': 'Latin America & Caribbean',
    'OMB': 'Asia',
    'OMC': 'Middle East, North Africa, Eastern Europe and Central Asia',
    'OMN': 'Eastern & Central Africa'
}


@python_2_unicode_compatible
class Country(LastUpdateDateModel):
    """
    Model for the country of origin.
    """
    iso_code = models.CharField(max_length=2, unique=True,
                                blank=False, null=False, db_index=True,
                                help_text='ISO 3166-1 alpha 2',
                                validators=[MinLengthValidator(2)])
    iso_code3 = models.CharField(max_length=3, unique=True,
                                 blank=False, null=False, db_index=True,
                                 help_text='ISO 3166-1 alpha 3',
                                 validators=[MinLengthValidator(3)])
    iso_num = models.CharField(max_length=3, unique=True, blank=False, null=False,
                               help_text='ISO 3166-1 numeric',
                               validators=[RegexValidator('\d\d\d')])
    undp = models.CharField(max_length=3, unique=True, blank=True, null=True,
                            help_text='UNDP code',
                            validators=[MinLengthValidator(3)])

    nato3 = models.CharField(max_length=3, unique=True, blank=True, null=True,
                             help_text='NATO3 code',
                             validators=[MinLengthValidator(3)])

    fips = models.CharField(max_length=255, blank=True, null=True,
                            help_text='fips code')

    itu = models.CharField(max_length=255, blank=True, null=True,
                           help_text='ITU code')

    icao = models.CharField(max_length=255, blank=True, null=True,
                            help_text='ICAO code')

    name = models.CharField(max_length=100, db_index=True)

    fullname = models.CharField(max_length=100, db_index=True)

    region = models.ForeignKey(UNRegion, blank=True, null=True, default=None,
                               on_delete=models.CASCADE)
    continent = models.CharField(choices=CONTINENTS, max_length=2)
    currency = models.ForeignKey(Currency, blank=True, null=True,
                                 on_delete=models.CASCADE)

    tld = models.CharField(help_text='Internet tld', max_length=5,
                           blank=True, null=True)
    phone_prefix = models.CharField(help_text='Phone prefix number',
                                    max_length=20, blank=True, null=True)

    timezone = TimeZoneField(blank=True, null=True, default=None)
    expired = models.DateField(blank=True, null=True, default=None)

    lat = models.DecimalField('Latitude', max_digits=18, decimal_places=12,
                              blank=True, null=True)
    lng = models.DecimalField('Longitude', max_digits=18, decimal_places=12,
                              blank=True, null=True)

    objects = CountryManager()

    fullname.alphabetic_filter = True

    class Meta:
        app_label = 'geo'
        verbose_name_plural = _('Countries')
        ordering = ['name']

    def __str__(self):
        return '%s (%s)' % (self.fullname, self.iso_code)

    def __contains__(self, item):
        if hasattr(item, 'country'):
            return item.country.iso_code == self.iso_code

    def clean(self):
        super(Country, self).clean()
        self.iso_code = self.iso_code.upper()
        self.iso_code3 = self.iso_code3.upper()

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.clean()
        super(Country, self).save(force_insert, force_update, using, update_fields)

    def sub(self, type):
        return self.areas.filter(type__name=type)


@python_2_unicode_compatible
class CountryNameTranslation(LastUpdateDateModel):
    """
    Model to store country name translation in different countries.
    """
    country = models.ForeignKey(Country,on_delete=models.CASCADE)
    language_iso_code = models.CharField(max_length=2, unique=True,
                                         blank=False, null=False, db_index=True,
                                         help_text='Language iso code', validators=[MinLengthValidator(2)])
    translation = models.CharField(max_length=255,
                                   blank=True, null=True, help_text='Translation')

    class Meta:
        app_label = 'geo'
        verbose_name_plural = _('Country Name Translations')
        ordering = ['country']

    def __str__(self):
        return '{0.country.name} - {0.translation} ({0.language_iso_code})'.format(self)


class AdministrativeAreaTypeManager(TreeManager):
    use_for_related_fields = True


@python_2_unicode_compatible
class AdministrativeAreaType(MPTTModel, LastUpdateDateModel):
    name = models.CharField(_('Name'), max_length=100, db_index=True)
    country = models.ForeignKey(Country, related_name='admins',
                                on_delete=models.CASCADE)
    parent = TreeForeignKey('self', null=True, blank=True,
                            related_name='children',
                            on_delete=models.CASCADE)

    objects = AdministrativeAreaTypeManager()

    class Meta:
        verbose_name = _('Administrative Area Type')
        verbose_name_plural = _('Administrative Area Types')
        app_label = 'geo'
        ordering = ['country', 'name', ]
        unique_together = (('country', 'name', 'parent'),)

    def __str__(self):
        return self.name

    def __contains__(self, item):
        if isinstance(item, AdministrativeAreaType) and item.is_child_node():
            return item.is_descendant_of(self)

    def clean(self):
        if self.parent == self:
            raise ValidationError(_('`%s` cannot contains same type') % self.parent)
        if self.parent:
            self.country_id = self.parent.country_id
        super(AdministrativeAreaType, self).clean()

    def save(self, *args, **kwargs):
        self.clean()
        super(AdministrativeAreaType, self).save(*args, **kwargs)


class AdministrativeAreaManager(TreeManager):
    use_for_related_fields = True

    def _create_tree_space(self, target_tree_id, num_trees=1):
        super(AdministrativeAreaManager, self)._create_tree_space(target_tree_id, num_trees)


@python_2_unicode_compatible
class AdministrativeArea(MPTTModel, LastUpdateDateModel):
    """ Administrative areas that can contains other AdministrativeArea and/or Location.
    """
    name = models.CharField(_('Name'), max_length=255, db_index=True)
    code = models.CharField(_('Code'), max_length=10,
                            blank=True, null=True, db_index=True,
                            help_text='ISO 3166-2 code')
    parent = TreeForeignKey('self', null=True,
                            blank=True, default=None, related_name='areas',
                            on_delete=models.CASCADE)
    country = models.ForeignKey(Country, related_name='areas',
                                on_delete=models.CASCADE)
    type = models.ForeignKey(AdministrativeAreaType, related_name='areas',
                             on_delete=models.CASCADE)

    objects = AdministrativeAreaManager()

    class Meta:
        verbose_name = _('Administrative Area')
        verbose_name_plural = _('Administrative Areas')
        unique_together = (('name', 'country', 'type', 'parent'),)
        app_label = 'geo'
        ordering = ['country', 'name', ]

    def __str__(self):
        return self.name

    def __repr__(self):
        return '<%s: %s>' % (self.type.name, self.name)

    def clean(self):
        if self.parent == self:
            raise ValidationError(_('`%s` cannot contains self') % self)
        if self.parent and self.parent.type == self.type:
            raise ValidationError(_('`%s` cannot contains same type') % self.parent.type)
        if (self.pk and self.parent) and self.parent in self:
            raise ValidationError(_('`%s` cannot contains `%s`') % (self, self.parent))
        super(AdministrativeArea, self).clean()

    def save(self, *args, **kwargs):
        if not self.country_id:
            if self.parent:
                self.country = self.parent.country
            else:
                self.country = self.type.country

        self.clean()
        super(AdministrativeArea, self).save(*args, **kwargs)

    def __contains__(self, item):
        if isinstance(item, AdministrativeArea) and item.is_child_node():
            return item.is_descendant_of(self)
        elif isinstance(item, Location) and item.area:
            return item.area == self or item.area.is_descendant_of(self)


class LocationTypeManager(models.Manager):
    use_for_related_fields = True


@python_2_unicode_compatible
class LocationType(LastUpdateDateModel):
    """Type of the location (city, village, place, locality, neighbourhood, etc.)
    This is not intended to contain anything inside it.
    """
    description = models.CharField(unique=True, max_length=100)
    objects = LocationTypeManager()

    class Meta:
        verbose_name_plural = _('Location Types')
        verbose_name = _('Location Type')
        app_label = 'geo'

    def __str__(self):
        return self.description


class LocationManager(models.Manager):
    use_for_related_fields = True

    def get_or_none(self, *args, **kwargs):
        try:
            return self.get(*args, **kwargs)
        except ObjectDoesNotExist:
            return None


@python_2_unicode_compatible
class Location(LastUpdateDateModel):
    """Administrative location (city, place everything with a name and Lat/Lng that
    is not intended to contain anything; use Areas for that).
    """
    NONE = 0
    COUNTRY = 10
    EXACT = 20

    ACCURACY = (
        (NONE, _('None')),
        (COUNTRY, _('Country')),
        (EXACT, _('Exact')))

    country = models.ForeignKey(Country,
                                db_index=True, blank=True, null=True,
                                related_name='locations',
                                on_delete=models.CASCADE)
    area = models.ForeignKey(AdministrativeArea,
                             db_index=True, blank=True, null=True,
                             related_name='locations',
                             on_delete=models.CASCADE)
    type = models.ForeignKey(LocationType,
                             blank=True, null=True,
                             related_name='locations',
                             on_delete=models.CASCADE)

    is_capital = models.BooleanField(default=False, help_text='True if is the capital of `country`')
    is_administrative = models.BooleanField(default=False, help_text='True if is administrative for `area`')

    name = models.CharField(_('Name'), max_length=255, db_index=True)
    loccode = models.CharField(_('UN LOCODE'), max_length=255,
                               db_index=True, blank=True, null=True)
    iata = models.CharField(_('IATA code (if exists)'), max_length=255,
                            db_index=True, blank=True, null=True)

    description = models.CharField(max_length=100, blank=True, null=True)
    lat = models.DecimalField(max_digits=19, decimal_places=16, blank=True, null=True)
    lng = models.DecimalField(max_digits=19, decimal_places=16, blank=True, null=True)
    acc = models.IntegerField(choices=ACCURACY, default=NONE,
                              blank=True, null=True,
                              help_text='Define the level of accuracy of lat/lng infos')

    geoname_id = models.IntegerField(_('Geoname'), blank=True, null=True)

    status = models.CharField(max_length=2,
                              blank=True, null=True,
                              choices=(
                                  ('AA', 'Approved by competent national government agency'),
                                  ('AC', 'Approved by Customs Authority'),
                                  ('AF', 'Approved by national facilitation body'),
                                  ('AI', 'Code adopted by international organisation (IATA or ECLAC)'),
                                  ('RL', 'Recognised location - Existence and representation of location name '
                                         'confirmed by check against nominated gazetteer or other reference work'),
                                  ('RN', 'Request from credible national sources for locations in their own country'),
                                  ('RQ', 'Request under consideration'),
                                  ('RR', 'Request rejected'),
                                  ('QQ', 'Original entry not verified since date indicated'),
                                  ('XX', 'Entry that will be removed from the next issue of UN/LOCODE'),
                              ))
    objects = LocationManager()

    class Meta:
        verbose_name_plural = _('Locations')
        verbose_name = _('Location')
        app_label = 'geo'
        ordering = ('country', 'name',)
        unique_together = (('area', 'name'), ('loccode', 'country'))

    def __str__(self):
        return u"{}, {} ({})".format(self.name, self.country, self.get_acc_display())

    def clean(self):
        if self.area and self.country and self.area.country != self.country:
            raise ValidationError('Selected area not in selected country')
        super(Location, self).clean()

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if not self.country_id:
            if self.area:
                self.country = self.area.country
        self.clean()
        super(Location, self).save(force_insert, force_update, using, update_fields)
