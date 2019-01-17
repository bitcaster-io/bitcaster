# -*- coding: utf-8 -*-
import logging

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as _UserAdmin
from django.utils.translation import gettext_lazy as _

from bitcaster.models import Address, ApiAuthToken, ApplicationTriggerKey, User

from .forms import UserCreationForm
from .inlines import ApiTokenInline
from .site import site

logger = logging.getLogger(__name__)


@admin.register(Address, site=site)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'address', 'dispatcher')


@admin.register(User, site=site)
class UserAdmin(_UserAdmin):
    inlines = [ApiTokenInline, ]
    # add_form_template = 'admin/auth/user/add_form.html'
    add_form = UserCreationForm
    # form = UserChangeForm
    list_display = ('email', 'name', 'is_staff',
                    'language', 'timezone')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups',)
    ordering = ('email',)

    fieldsets = (
        (None, {'fields': (('email', 'password'),)}),
        (_('Personal info'), {'fields': (('name', 'friendly_name'),
                                         ('language',),
                                         ('country', 'timezone'))}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       # 'groups', 'user_permissions'
                                       )}),
        (_('Important dates'), {'fields': (('last_login',
                                            'last_password_change',
                                            'date_joined'),)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (('email', 'language'),
                       ('country', 'timezone'),
                       ('password1', 'password2'),),
        }),
    )

    # def get_changeform_initial_data(self, request):
    #     initial = super().get_changeform_initial_data(request)
    #     remote_ip = get_client_ip(request)
    #     initial['language'] = request.LANGUAGE_CODE
    #     if remote_ip:
    #         from geolite2 import geolite2
    #         reader = geolite2.reader()
    #         match = reader.get(remote_ip)
    #         if match:
    #             # code = match['country']['iso_code'].lower()
    #             # c = pycountry.languages.get(alpha_2=code)
    #             # initial['language'] = c.alpha_2.lower()
    #             initial['country'] = match['country']['iso_code']
    #             initial['timezone'] = match['location']['time_zone']
    #     return initial


@admin.register(ApiAuthToken, site=site)
class ApiAuthTokenAdmin(admin.ModelAdmin):
    list_display = ('application', 'user', 'token', 'enabled')


@admin.register(ApplicationTriggerKey, site=site)
class ApplicationTriggerKeyAdmin(admin.ModelAdmin):
    list_display = ('application', 'token', 'enabled')
