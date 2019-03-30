import logging

from constance import config
from django.contrib.auth import login, logout
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.hashers import make_password
from django.db import transaction
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.functional import cached_property
from django.utils.translation import ugettext as _
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import CreateView, RedirectView
from django.views.generic.detail import SingleObjectMixin
from strategy_field.utils import fqn

from bitcaster import messages
from bitcaster.framework.db.fields import ROLES
from bitcaster.middleware.exception import RedirectToRefererResponse
from bitcaster.models import Invitation, Organization, OrganizationMember, User
from bitcaster.otp import totp
from bitcaster.web.forms import UserInviteRegistrationForm
from bitcaster.web.views.base import (BitcasterBaseCreateView,
                                      BitcasterBaseDeleteView,)
from bitcaster.web.views.mixins import MessageUserMixin

logger = logging.getLogger(__name__)


class InviteMixin:
    model = Invitation


class InvitationAccept(MessageUserMixin, CreateView):
    model = User
    form_class = UserInviteRegistrationForm
    template_name = 'bitcaster/registration/user_welcome.html'

    @cached_property
    def selected_organization(self):  # returns selected office and caches the office
        organization = Organization.objects.get(slug=self.kwargs['org'])
        return organization

    def check_perms(self, *args, **kwargs):
        return True

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            logout(request)
            # return HttpResponseBadRequest("User already logged")
        return super().dispatch(request, *args, **kwargs)

    @method_decorator(sensitive_post_parameters())
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        with transaction.atomic():
            user = User.objects.create(email=form.cleaned_data['email'],
                                       is_active=True,
                                       friendly_name=form.cleaned_data['friendly_name'],
                                       password=make_password(form.cleaned_data['password']),
                                       )
            self.membership.user = user
            self.membership.date_enrolled = timezone.now()
            self.membership.save()
            login(self.request, user, backend=fqn(ModelBackend))
            assert self.request.user == user

        if self.membership.role in [ROLES.OWNER, ROLES.ADMIN]:
            url = reverse('org-dashboard', args=[self.selected_organization.slug])
        else:
            url = reverse('me', args=[self.selected_organization.slug])
        logger.debug(f'Invitation accepted by user {user.email} with role {self.membership.role}. '
                     f'Redirecting to {url}')
        return HttpResponseRedirect(url)

    def form_invalid(self, form):
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        if self.membership:
            kwargs['membership'] = self.membership
            kwargs['invitation_id'] = self.membership.pk  # this is required by oauth
            return super().get_context_data(**kwargs)
        else:
            return {}

    def get_initial(self):
        return {'email': self.membership.email,
                'friendly_name': self.membership.email}

    @cached_property
    def membership(self):
        pk = self.kwargs['pk']
        return OrganizationMember.objects.filter(pk=pk,
                                                 organization__slug=self.kwargs['org']).first()

    def get(self, request, **kwargs):
        check = kwargs['check']
        if totp.verify(check, valid_window=config.INVITATION_EXPIRE):
            return super(InvitationAccept, self).get(request, **kwargs)
        self.message_user(_('Invite expired'), messages.ERROR)
        return HttpResponseRedirect('/')


class InvitationSend(InviteMixin, MessageUserMixin, SingleObjectMixin, RedirectView):
    def get(self, request, *args, **kwargs):
        membership = self.get_object()
        try:
            membership.send_email()
            self.message_user(_('Email sending scheduled'))
        except Exception as e:
            logger.exception(e)
            self.message_user(_('Error sending email'), messages.ERROR)
        return RedirectToRefererResponse(request)


class InvitationCreate(InviteMixin, BitcasterBaseCreateView):
    title = _('Invite people')

    def get_parent_instance(self):
        raise NotImplementedError

    def get_context_data(self, **kwargs):
        data = super(InviteMixin, self).get_context_data(**kwargs)
        data['invitations'] = data['form']
        return data

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.instance = self.get_parent_instance()
        return form

    def form_invalid(self, form):
        self.message_user(_('invalid'), messages.WARNING)
        return super(InviteMixin, self).form_invalid(form)

    def form_valid(self, form):
        form.instance = self.get_parent_instance()
        invitations = form.save()
        for invitation in invitations:
            invitation.send_email()
        self.message_user(_('Email sending scheduled'))
        return super(InviteMixin, self).form_valid(form)


class InvitationDelete(InviteMixin, BitcasterBaseDeleteView):
    title = _('Cancel invitation')
    message = _('Invitation to <strong>%(object)s</strong> will be canceled')
    user_message = _('Invitation Canceled')

#
# class InviteSend(InviteMixin, BitcasterBaseUpdateView):
#     fields = ()
#     def form_valid(self, form):
#         membership = self.get_object()
#         try:
#             membership.send_email()
#             self.message_user(_('Email sending scheduled'))
#         except Exception as e:
#             logger.exception(e)
#             self.message_user(_('Error sending email'), messages.ERROR)
#         return super().form_valid(form)
