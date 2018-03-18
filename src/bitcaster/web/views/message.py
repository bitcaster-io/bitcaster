# -*- coding: utf-8 -*-
import logging

from django.urls import reverse
from django.utils.translation import gettext as _
from django.views.generic import ListView

from bitcaster.models import Message
from bitcaster.web.forms import MessageForm
from bitcaster.web.views import (CreateView, DeleteView, MessageUserMixin,
                                 SelectedApplicationMixin, UpdateView, )

logger = logging.getLogger(__name__)


class MessageMixin(SelectedApplicationMixin, MessageUserMixin):
    model = Message

    def get_success_url(self):
        return reverse("app-message-list",
                       args=[self.selected_organization.slug,
                             self.selected_application.slug])

    def get_queryset(self):
        return self.selected_application.messages.all()


class MessageFormMixin:
    form_class = MessageForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({"application": self.selected_application})
        return kwargs

    def get_context_data(self, **kwargs):
        kwargs["title"] = self.title
        return super().get_context_data(**kwargs)


class MessageList(SelectedApplicationMixin, ListView):
    model = Message

    def get_queryset(self):
        return self.selected_application.messages.all()


class MessageUpdate(MessageMixin, MessageFormMixin, UpdateView):
    title = "Edit Message"

    def get_context_data(self, **kwargs):
        return super().get_context_data(save_label=_("Save Message"),
                                        **kwargs)


class MessageCreate(MessageMixin, MessageFormMixin, CreateView):
    title = "Create Message"

    def get_context_data(self, **kwargs):
        return super().get_context_data(save_label=_("Create Message"),
                                        **kwargs)


class MessageDelete(MessageMixin, DeleteView):
    pass
