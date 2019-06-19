import logging

from crashlog.middleware import process_exception
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from sentry_sdk import capture_exception, push_scope

from bitcaster.exceptions import FilteringError, PermissionDenied
from bitcaster.models import Notification
from bitcaster.models.audit import AuditLogEntry
from bitcaster.state import state
from bitcaster.utils.filtering import FilterParser
from bitcaster.utils.language import parse_bool
from bitcaster.utils.reflect import fqn
from bitcaster.utils.wsgi import get_client_ip
from bitcaster.web import messages
from bitcaster.web.decorators import authorized_or_403
from bitcaster.web.templatetags.bitcaster import (verbose_name,
                                                  verbose_name_plural,)

logger = logging.getLogger(__name__)


class SecuredViewMixin:
    permissions = []
    target = ''

    # @lru_cache()
    def check_perms(self, request, obj=None, raise_exception=False):
        if self.permissions is None:
            return True
        if obj is None:
            if not self.target:
                raise ValueError('View must set `target` attribute')
            obj = getattr(self, self.target)
        for perm in self.permissions:
            if request.user.has_perm(perm, obj):
                return True
        if raise_exception:
            raise PermissionDenied(self, obj)
        return False

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class LogAuditMixin:

    def audit(self, target, event, **kwargs):
        if self.request.user.is_authenticated:
            kwargs.setdefault('organization', self.selected_organization)
            kwargs.setdefault('actor', self.request.user)
            kwargs.setdefault('actor_label', kwargs['actor'].display_name)
            kwargs.setdefault('target_label', str(target))
            kwargs.setdefault('ip_address', get_client_ip(state.request))

            AuditLogEntry.objects.create(target=target,
                                         event=event,
                                         **kwargs)


class SidebarMixin:

    def get_context_data(self, **kwargs):
        sidebar_class = self.request.COOKIES.get('sidebar')
        return super().get_context_data(sidebar=sidebar_class, **kwargs)


class TitleMixin:
    title = 'xx'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        vars = dict(ctx)
        if hasattr(self, 'model'):
            vars.update(verbose_name=verbose_name(self.model),
                        verbose_name_plural=verbose_name_plural(self.model))
        # if 'object' in ctx:
        #     vars['object'] = ctx

        ctx['title'] = mark_safe(self.title % vars)
        return ctx


class BitcasterSingleObjectMixin:
    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        vars = dict(kwargs)
        vars.update(verbose_name=verbose_name(self.object), object=self.object)
        return kwargs


@method_decorator(authorized_or_403(lambda u: u.is_superuser), name='dispatch')
class SuperuserViewMixin(SecuredViewMixin):
    pass


class MessageUserMixin:
    def alarm(self, alarm, level=messages.ERROR, extra_tags='',
              fail_silently=False):
        messages.add_alarm(self.request, level, mark_safe(alarm),
                           extra_tags=extra_tags,
                           fail_silently=fail_silently)

    def message_user(self, message, level=messages.INFO, fail_silently=False):
        messages.add_message(self.request, level, mark_safe(message),
                             fail_silently=fail_silently)

    def error_user(self, message, level=messages.ERROR, fail_silently=False):
        messages.add_message(self.request, level, mark_safe(message),
                             fail_silently=fail_silently)

    def warn_user(self, message, level=messages.ERROR, fail_silently=False):
        messages.add_message(self.request, level, mark_safe(message),
                             fail_silently=fail_silently)


class BitcasterBaseViewMixin(TitleMixin, MessageUserMixin):
    pass


class FilterQuerysetMixin:
    filter_fieldmap = {}
    search_fields = []
    filter_url_kwarg = 'filter'

    def get_parser(self):
        return FilterParser(self, self.filter_fieldmap, self.search_fields)

    def _parse_bool(self, parser, keyword, value):
        parser.kwargs[keyword] = parse_bool(value)

    def filter_queryset(self, queryset):
        self.active_filter = [], {}
        self.filtering_errors = []
        try:
            target = self.request.GET.get(self.filter_url_kwarg)
            args, kw, errors = self.get_parser().parse(target)
            if args:
                queryset = queryset.filter(args, **kw)
            else:
                queryset = queryset.filter(**kw)
            self.active_filter = args, kw
            self.filtering_errors.extend(errors)
        except Exception as e:
            self.filtering_errors.append('Syntax error (missing operator) in query expression. Data not filtered')
            self.filtering_errors.append(str(e))
            logger.exception(e)
            process_exception(e)
            with push_scope() as scope:
                scope.set_tag('view', fqn(self))
                capture_exception()

        return queryset


class NotificationLogMixin(FilterQuerysetMixin):
    search_fields = ['channel__name__iexact']
    filter_fieldmap = {
        # Translators: UserNotificationLogView.filter_fieldmap
        _('channel'): 'channel__name__iexact',
        _('occurence'): 'occurence_id',
        '#': 'occurence_id',
        _('application'): 'application__name__istartswith',
        _('event'): 'event__name__istartswith',
        _('status'): '_filter_status',
        _('user'): 'subscription__subscriber__email__istartswith',
        _('subscriber'): 'subscription__subscriber__email__istartswith',
    }

    def _filter_status(self, parser, keyword, value):
        code = [c[0] for c in Notification.STATUSES if c[1].lower() == value]
        if code:
            parser.kwargs['status'] = code[0]
        else:
            raise FilteringError('status', value)
