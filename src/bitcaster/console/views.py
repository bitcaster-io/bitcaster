from typing import Any

from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db.models import QuerySet
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie
from django.views.generic import DetailView, TemplateView, UpdateView
from django.views.generic.base import ContextMixin
from timezone_field import TimeZoneFormField

from bitcaster.console.utils import (
    get_user_latest_display_time,
    get_user_latest_notify_time,
    set_user_latest_display_time,
    set_user_latest_notify_time,
)
from bitcaster.forms.unfold import UnfoldAdminSelectWidget, UnfoldForm
from bitcaster.models import User, UserMessage
from bitcaster.web.views import UnfoldViewMixin


class MessageForm(forms.ModelForm[UserMessage]):
    check = forms.BooleanField(required=False)

    class Meta:
        model = UserMessage
        fields = ("check",)


MessageFormSet = forms.modelformset_factory(UserMessage, MessageForm, extra=0)


class UserConsoleMixin(UnfoldViewMixin, ContextMixin):
    pass


# @method_decorator(cache_page(60 * 1), name='dispatch')
# @method_decorator(vary_on_cookie, name='dispatch')
class UserConsoleIndexView(UserConsoleMixin, LoginRequiredMixin, TemplateView):
    template_name = "bitcaster/console/index.html"
    paginate_by = 25

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        ctx = super().get_context_data(**kwargs)
        qs = self.request.user.bitcaster_messages.order_by("-created")

        paginator = Paginator(qs, self.paginate_by)
        page_number = self.request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        last_seen = get_user_latest_display_time(self.request.user.pk)  # type: ignore[arg-type]
        last_notify = get_user_latest_notify_time(self.request.user.pk)  # type: ignore[arg-type]

        set_user_latest_display_time(self.request.user.pk)  # type: ignore[arg-type]
        set_user_latest_notify_time(self.request.user.pk)  # type: ignore[arg-type]
        ctx.update(
            user=self.request.user,
            messages=MessageFormSet(queryset=page_obj.object_list),  # type: ignore[arg-type]
            page_obj=page_obj,
            last_seen=last_seen,
            last_notify=last_notify,
        )
        return ctx


@method_decorator(cache_page(60 * 60), name="dispatch")
@method_decorator(vary_on_cookie, name="dispatch")
class UserConsoleDetailView(UserConsoleMixin, LoginRequiredMixin, DetailView[UserMessage]):
    template_name = "bitcaster/console/detail.html"
    model = UserMessage

    def get_object(self, queryset: QuerySet["UserMessage"] | None = None) -> UserMessage:
        obj = super().get_object(queryset)
        if not obj.read:
            obj.read = timezone.now()
            obj.save()
        return obj


class UserPrefFrom(UnfoldForm, forms.ModelForm[User]):
    timezone = TimeZoneFormField(widget=UnfoldAdminSelectWidget)

    class Meta:
        model = User
        fields = ("timezone", "date_format", "time_format")


class UserConsoleUserPrefsView(UserConsoleMixin, LoginRequiredMixin, UpdateView[User, UserPrefFrom]):
    template_name = "bitcaster/console/prefs.html"
    form_class = UserPrefFrom
    model = User
    success_url = "."

    def get_object(self, queryset: QuerySet["User"] | None = None) -> User:
        return self.request.user  # type: ignore[return-value]
