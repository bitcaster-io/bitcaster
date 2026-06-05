from typing import Any, cast

from timezone_field import TimeZoneFormField

from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db.models import QuerySet
from django.utils import timezone
from django.views.generic import DetailView, TemplateView, UpdateView
from django.views.generic.base import ContextMixin

from bitcaster.forms.unfold import UnfoldAdminSelectWidget, UnfoldForm
from bitcaster.models import Application, Event, User, UserMessage
from bitcaster.web.views import UnfoldViewMixin

from .utils import (
    get_user_latest_display_time,
    get_user_latest_notify_time,
    set_user_latest_display_time,
    set_user_latest_notify_time,
)


class MessageForm(forms.ModelForm[UserMessage]):
    check = forms.BooleanField(required=False)

    class Meta:
        model = UserMessage
        fields = ("check",)


MessageFormSet = forms.modelformset_factory(UserMessage, MessageForm, extra=0)


class UserConsoleMixin(UnfoldViewMixin, ContextMixin):
    pass


class UserConsoleIndexView(UserConsoleMixin, LoginRequiredMixin, TemplateView):
    template_name = "bitcaster/console/index.html"
    paginate_by = 25

    def get_queryset(self) -> QuerySet[UserMessage]:
        user = cast("User", self.request.user)
        qs = user.bitcaster_messages.order_by("-created")
        status = self.request.GET.get("status")
        if status == "unread":
            qs = qs.filter(read__isnull=True)
        elif status == "read":
            qs = qs.filter(read__isnull=False)
        if application := self.request.GET.get("application"):
            qs = qs.filter(event__application_id=application)
        if event := self.request.GET.get("event"):
            qs = qs.filter(event_id=event)
        return qs

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        ctx = super().get_context_data(**kwargs)
        qs = self.get_queryset()

        paginator = Paginator(qs, self.paginate_by)
        page_number = self.request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        last_seen = get_user_latest_display_time(self.request.user.pk)  # type: ignore[arg-type]
        last_notify = get_user_latest_notify_time(self.request.user.pk)  # type: ignore[arg-type]

        set_user_latest_display_time(self.request.user.pk)  # type: ignore[arg-type]
        set_user_latest_notify_time(self.request.user.pk)  # type: ignore[arg-type]

        current_application = self.request.GET.get("application")
        current_event = self.request.GET.get("event")
        applications = Application.objects.filter(events__usermessage__user=self.request.user).distinct()
        events = Event.objects.none()
        if current_application:
            events = Event.objects.filter(
                application_id=current_application,
                usermessage__user=self.request.user,
            ).distinct()

        ctx.update(
            user=self.request.user,
            user_messages=MessageFormSet(queryset=page_obj.object_list),  # type: ignore[arg-type]
            page_obj=page_obj,
            last_seen=last_seen,
            details_url="console:detail",
            last_notify=last_notify,
            current_status=self.request.GET.get("status", "all"),
            applications=applications,
            events=events,
            current_application=current_application,
            current_event=current_event,
        )
        return ctx


class UserConsoleDetailView(UserConsoleMixin, LoginRequiredMixin, DetailView[UserMessage]):
    template_name = "bitcaster/console/detail.html"
    model = UserMessage

    def get_object(self, queryset: QuerySet["UserMessage"] | None = None) -> UserMessage:
        obj = super().get_object(queryset)
        if not obj.read:
            obj.read = timezone.now()
            obj.save()
        return obj


class UserPrefForm(UnfoldForm, forms.ModelForm[User]):
    timezone = TimeZoneFormField(widget=UnfoldAdminSelectWidget)

    class Meta:
        model = User
        fields = ("timezone", "date_format", "time_format")


class UserConsoleUserPrefsView(UserConsoleMixin, LoginRequiredMixin, UpdateView[User, UserPrefForm]):
    template_name = "bitcaster/console/prefs.html"
    form_class = UserPrefForm
    model = User
    success_url = "."

    def get_object(self, queryset: QuerySet["User"] | None = None) -> User:
        return cast("User", self.request.user)
