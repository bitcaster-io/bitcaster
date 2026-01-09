from typing import Any

from django import forms
from django.db.models import QuerySet
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie
from django.views.generic import DetailView, TemplateView

from bitcaster.console.utils import (
    get_user_latest_display_time,
    set_user_latest_display_time,
    set_user_latest_notify_time,
)
from bitcaster.models import UserMessage


class MessageForm(forms.ModelForm[UserMessage]):
    check = forms.BooleanField(required=False)

    class Meta:
        model = UserMessage
        fields = ("check",)


MessageFormSet = forms.modelformset_factory(UserMessage, MessageForm, extra=0)


# @method_decorator(cache_page(60 * 1), name='dispatch')
# @method_decorator(vary_on_cookie, name='dispatch')
class ConsoleIndexView(TemplateView):
    template_name = "bitcaster/console/index.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        ctx = super().get_context_data(**kwargs)
        qs = self.request.user.bitcaster_messages.order_by("-created")
        last_seen = get_user_latest_display_time(self.request.user.pk)  # type: ignore[arg-type]
        set_user_latest_display_time(self.request.user.pk)  # type: ignore[arg-type]
        set_user_latest_notify_time(self.request.user.pk)  # type: ignore[arg-type]
        ctx.update(user=self.request.user, messages=MessageFormSet(queryset=qs), last_seen=last_seen)
        return ctx


@method_decorator(cache_page(60 * 60), name="dispatch")
@method_decorator(vary_on_cookie, name="dispatch")
class ConsoleDetailView(DetailView[UserMessage]):
    template_name = "bitcaster/console/detail.html"
    model = UserMessage

    def get_object(self, queryset: QuerySet["UserMessage"] | None = None) -> UserMessage:
        obj = super().get_object(queryset)
        if not obj.read:
            obj.read = timezone.now()
            obj.save()
        return obj
