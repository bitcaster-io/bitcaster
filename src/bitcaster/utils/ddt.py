# pragma: no cover
from debug_toolbar.panels import Panel
from debug_toolbar.utils import get_name_from_obj
from django.template.loader import render_to_string
from django.urls import resolve
from django.utils.translation import ugettext_lazy as _

from bitcaster.models import Application, Organization


class UserInfoPanel(Panel):
    name = 'Bitcaster'
    has_content = True

    @property
    def nav_title(self):
        return _('Bitcaster')

    @property
    def url(self):
        return ''

    @property
    def title(self):
        return _('Bitcaster')

    def process_request(self, request):
        self.request = request
        return super().process_request(request)

    @property
    def nav_subtitle(self):
        return self.is_authenticated(self.request) and self.request.user

    template = 'bitcaster/ddt/userinfo.html'

    def parse_url(self):
        current = self.request.path
        return current

    @property
    def content(self):
        view_info = {
            'url': self.parse_url(),
            'user': self.request.user,
            'request': self.request,
            'application': None,
            'organization': None,
            'perms': self.request.user.get_all_permissions(),
            'view_func': _('<no view>'),
            'view_args': 'None',
            'view_kwargs': 'None',
            'view_urlname': 'None',
        }
        try:
            match = resolve(self.request.path)
            func, args, kwargs = match
            view_info['view_func'] = get_name_from_obj(func)
            view_info['view_args'] = args
            view_info['view_kwargs'] = kwargs
            view_info['view_urlname'] = getattr(match, 'url_name', _('<unavailable>'))
        except Exception:
            pass
        org_slug = view_info.get('view_kwargs', {}).get('org')
        if org_slug:
            view_info['organization'] = Organization.objects.get(slug=org_slug)
        app_slug = view_info.get('view_kwargs', {}).get('app')
        if app_slug:
            view_info['application'] = Application.objects.get(slug=app_slug)

        return render_to_string(self.template, view_info)

    def is_authenticated(self, request):
        return request.user.is_authenticated

    def process_response(self, request, response):
        self.request = request

    @classmethod
    def get_urls(cls):
        return ()
