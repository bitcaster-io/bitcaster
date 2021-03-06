import logging

from django import forms
from django.forms import inlineformset_factory
from django.utils.translation import gettext_lazy as _

from bitcaster.models import Event, Message
from bitcaster.web import messages
from bitcaster.web.forms import MessageForm
from bitcaster.web.views.base import BitcasterBaseUpdateView

from .event import EventFormMixin, EventMixin

logger = logging.getLogger(__name__)


# class MessageMixin(SelectedApplicationMixin, MessageUserMixin):
#     model = Message
#
#     def get_success_url(self):
#         return reverse('app-messages',
#                        args=[self.selected_organization.slug,
#                              self.selected_application.slug])

# def get_queryset(self):
#     return self.selected_application.messages.all()


# class MessageFormMixin:
#     form_class = MessageForm
#
#     def get_form_kwargs(self):
#         kwargs = super().get_form_kwargs()
#         kwargs.update({'application': self.selected_application})
#         return kwargs
#

class MessageInlineFormSet(forms.BaseInlineFormSet):
    def get_queryset(self):
        if not hasattr(self, '_queryset'):
            self._queryset = self.queryset.select_related('channel',
                                                          'event')
            if not self._queryset.ordered:
                self._queryset = self._queryset.order_by('channel__name')
        return self._queryset
    # def clean(self):
    #     forms_to_delete = self.deleted_forms
    #     at_least_one_enabled = False
    #     for form in self.forms:
    #         if form not in forms_to_delete:
    #             print(111, form.instance.channel.handler.validate_message())
    #     return super().clean()


# class MessageList(SelectedApplicationMixin, ListView):
#     model = Message
#
#     def get_queryset(self):
#         return self.selected_application.messages.all()
#
#
# class MessageUpdate(MessageMixin, MessageFormMixin, BitcasterBaseUpdateView):
#     title = 'Edit Message'
#
# def get_context_data(self, **kwargs):
#     return super().get_context_data(save_label=_('Save Message'),
#                                     **kwargs)
#
#
# class MessageCreate(MessageMixin, MessageFormMixin, BitcasterBaseCreateView):
# title = 'Create Message'
#
# def get_context_data(self, **kwargs):
#     return super().get_context_data(save_label=_('Create Message'),
#                                     **kwargs)


# class MessageDelete(MessageMixin, BitcasterBaseDeleteView):
#     pass


class EventMessages(EventMixin, EventFormMixin, BitcasterBaseUpdateView):
    template_name = 'bitcaster/application/events/messages.html'

    title = _('event messages')

    # def get_context_data(self, **kwargs):
    #     return super().get_context_data(**kwargs)

    def get_form_kwargs(self):
        ret = super().get_form_kwargs()
        ret.pop('application')
        return ret

    def get_form_class(self):
        form = type('MessageForm', (MessageForm,), dict())
        return inlineformset_factory(Event, Message, form,
                                     formset=MessageInlineFormSet,
                                     extra=0)

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()
        formset = form_class(**self.get_form_kwargs())
        # event = self.get_object()
        for form in formset:
            # form.event = event
            form.has_subject = form.instance.channel.handler.message_class.has_subject
        # frm.instance = self.get_object()

        return formset

    def form_valid(self, form):
        self.message_user('Saved')
        return super().form_valid(form)

    #
    # def post(self, request, *args, **kwargs):
    #     return super().post(request, *args, **kwargs)
    #
    def form_invalid(self, form):
        self.message_user('Invalid', messages.ERROR)
        return super().form_invalid(form)
