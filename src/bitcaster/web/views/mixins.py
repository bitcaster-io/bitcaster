# -*- coding: utf-8 -*-
import logging

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.utils.safestring import mark_safe
from django.views.generic.base import TemplateResponseMixin

from bitcaster import messages
from bitcaster.security import authorized_or_403

logger = logging.getLogger(__name__)


class SecuredViewMixin:
    def check_perms(self, request, obj=None, raise_exception=False):
        return request.user.has_perm('', obj)

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


@method_decorator(authorized_or_403(lambda u: u.is_superuser), name='dispatch')
class SuperuserViewMixin(SecuredViewMixin):
    def check_perms(self, request, obj=None, raise_exception=False):
        return request.user.has_perm(obj)


class MessageUserMixin:
    def alarm(self, alarm, level=messages.ERROR, extra_tags='',
              fail_silently=False):
        messages.add_alarm(self.request, level, mark_safe(alarm),
                           extra_tags=extra_tags,
                           fail_silently=fail_silently)

    def message_user(self, message, level=messages.INFO, extra_tags='',
                     fail_silently=False):
        messages.add_message(self.request, level, mark_safe(message),
                             extra_tags=extra_tags,
                             fail_silently=fail_silently)

    def error_user(self, message, level=messages.ERROR, extra_tags='keep',
                   fail_silently=False):
        messages.add_message(self.request, level, mark_safe(message),
                             extra_tags=extra_tags,
                             fail_silently=fail_silently)


class BitcasterBaseViewMixin(MessageUserMixin):
    pass


class BitcasterSingleObjectTemplateResponseMixin(TemplateResponseMixin):
    def get_context_data(self, **kwargs):
        kwargs['opts'] = self.model._meta
        return super().get_context_data(**kwargs)

    # template_name_base = None
    # def get_template_names(self):
    #     try:
    #         if self.template_name is None:
    #             raise ImproperlyConfigured(
    #                 'TemplateResponseMixin requires either a definition of '
    #                 "'template_name' or an implementation of 'get_template_names()'")
    #         names = [self.template_name]
    #     except ImproperlyConfigured:
    #         names = []
    #
    #         # If self.template_name_field is set, grab the value of the field
    #         # of that name from the object; this is the most specific template
    #         # name, if given.
    #         if self.object and self.template_name_field:
    #             name = getattr(self.object, self.template_name_field, None)
    #             if name:
    #                 names.insert(0, name)
    #
    #         if self.template_name_base:
    #             base = 'bitcaster/%s' % self.template_name_base
    #         else:
    #             base = 'bitcaster'
    #
    #         # The least-specific option is the default <app>/<model>_detail.html;
    #         # only use this if the object in question is a model.
    #         if isinstance(self.object, models.Model):
    #             object_meta = self.object._meta
    #             names.append('%s/%s%s.html' % (
    #                 base,
    #                 object_meta.model_name,
    #                 self.template_name_suffix
    #             ))
    #         elif getattr(self, 'model', None) is not None and issubclass(self.model, models.Model):
    #             names.append('%s/%s%s.html' % (
    #                 base,
    #                 self.model._meta.model_name,
    #                 self.template_name_suffix
    #             ))
    #
    #         # If we still haven't managed to find any template names, we should
    #         # re-raise the ImproperlyConfigured to alert the user.
    #         if not names:
    #             raise
    #
    #     return names
