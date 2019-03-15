import logging

from django.utils.translation import ugettext as _

from bitcaster.models.invitation import Invitation
from bitcaster.web.forms.invitations import ApplicationInvitationFormSet
from bitcaster.web.views.invitations import (InvitationCreate,
                                             InvitationDelete, InvitationSend,)

from .app import ApplicationBaseView

logger = logging.getLogger(__name__)


class ApplicationInvitationMixin(ApplicationBaseView):
    model = Invitation

    def get_success_url(self):
        return self.selected_application.urls.subscriptions

    def get_queryset(self):
        return self.selected_application.invitations


class ApplicationInvite(ApplicationInvitationMixin, InvitationCreate):
    form_class = ApplicationInvitationFormSet
    template_name = 'bitcaster/application/subscriptions/invite.html'
    title = _('Invite people')

    def get_parent_instance(self):
        return self.selected_application
    #
    # def get_form(self, form_class=None):
    #     form = super().get_form(form_class)
    #     form.instance = self.get_parent_instance()
    #     return form
    #
    # def form_invalid(self, form):
    #     self.message_user(_('invalid'), messages.WARNING)
    #     return super(ApplicationInvite, self).form_invalid(form)
    #
    # def form_valid(self, form):
    #     form.instance = self.selected_application
    #     form.save()
    #     return super(ApplicationInvite, self).form_valid(form)


# class InviteAccept(MessageUserMixin, CreateView):
#     model = User
#     form_class = UserInviteRegistrationForm
#     template_name = 'bitcaster/registration/user_welcome.html'
#
#     @cached_property
#     def selected_organization(self):  # returns selected office and caches the office
#         organization = Organization.objects.get(slug=self.kwargs['org'])
#         return organization
#
#     def check_perms(self, *args, **kwargs):
#         return True
#
#     def dispatch(self, request, *args, **kwargs):
#         if request.user.is_authenticated:
#             logout(request)
#             # return HttpResponseBadRequest("User already logged")
#         return super().dispatch(request, *args, **kwargs)
#
#     @method_decorator(sensitive_post_parameters())
#     def post(self, request, *args, **kwargs):
#         return super().post(request, *args, **kwargs)
#
#     def form_valid(self, form):
#         with transaction.atomic():
#             user = User.objects.create(email=form.cleaned_data['email'],
#                                        is_active=True,
#                                        friendly_name=form.cleaned_data['friendly_name'],
#                                        password=make_password(form.cleaned_data['password']),
#                                        )
#             self.membership.user = user
#             self.membership.date_enrolled = timezone.now()
#             self.membership.save()
#             login(self.request, user, backend=fqn(ModelBackend))
#             assert self.request.user == user
#             audit_log(self.request, AuditEvent.MEMBER_ACCEPT,
#                       organization=self.selected_organization,
#                       role=self.membership.get_role_display(),
#                       invited_by=self.membership.invited_by.email)
#
#         if self.membership.role in [Role.OWNER, Role.ADMIN]:
#             url = reverse('org-dashboard', args=[self.selected_organization.slug])
#         else:
#             url = reverse('me', args=[self.selected_organization.slug])
#         logger.debug(f'Invitation accepted by user {user.email} with role {self.membership.role}. '
#                      f'Redirecting to {url}')
#         return HttpResponseRedirect(url)
#
#     def form_invalid(self, form):
#         return super().form_invalid(form)
#
#     def get_context_data(self, **kwargs):
#         if self.membership:
#             kwargs['membership'] = self.membership
#             kwargs['invitation_id'] = self.membership.pk  # this is required by oauth
#             return super().get_context_data(**kwargs)
#         else:
#             return {}
#
#     def get_initial(self):
#         return {'email': self.membership.email,
#                 'friendly_name': self.membership.email}
#
#     @cached_property
#     def membership(self):
#         pk = self.kwargs['pk']
#         return OrganizationMember.objects.filter(pk=pk,
#                                                  organization__slug=self.kwargs['org']).first()
#
#     def get(self, request, **kwargs):
#         check = kwargs['check']
#         if totp.verify(check, valid_window=config.INVITATION_EXPIRE):
#             return super(InviteAccept, self).get(request, **kwargs)
#         self.message_user(_('Invite expired'), messages.ERROR)
#         return HttpResponseRedirect('/')


# class InviteSend(ApplicationBaseView, BitcasterBaseUpdateView):
#     fields = ()
#
#     def get_success_url(self):
#         return reverse('org-members', args=[self.selected_organization.slug])
#
#     def get_queryset(self):
#         return self.selected_organization.memberships.all()
#
#     def form_valid(self, form):
#         membership = self.get_object()
#         try:
#             membership.send_email()
#             self.message_user(_('Email sending scheduled'))
#         except Exception as e:
#             logger.exception(e)
#             self.message_user(_('Error sending email'), messages.ERROR)
#         return super().form_valid(form)


class ApplicationInvitationDelete(ApplicationInvitationMixin, InvitationDelete):
    pass
    # title = _('Cancel invitation')
    # message = _('Invitation to <strong>%(object)s</strong> will be canceled')
    # user_message = _('Invitation Canceled')


class ApplicationInvitationSend(ApplicationInvitationMixin, InvitationSend):
    pass
