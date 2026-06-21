from typing import TYPE_CHECKING

import pytest

from django.urls import reverse
from django.utils import timezone

if TYPE_CHECKING:  # pragma: no cover
    from bitcaster.models import Application, Event, User, UserMessage

pytestmark = [pytest.mark.xdist_group(name="console_view")]


@pytest.fixture
def message() -> "UserMessage":
    from testutils.factories import UserMessageFactory

    return UserMessageFactory.create()


@pytest.fixture
def application() -> "Application":
    from testutils.factories import ApplicationFactory

    return ApplicationFactory.create()


@pytest.fixture
def events(user, application) -> "tuple[Event, Event]":
    from testutils.factories import EventFactory

    event1 = EventFactory.create()
    event2 = EventFactory.create()
    return event1, event2


@pytest.fixture
def messages(user, events) -> "tuple[UserMessage, UserMessage]":
    from testutils.factories import UserMessageFactory

    msg1 = UserMessageFactory.create(user=user, event=events[0])
    msg2 = UserMessageFactory.create(user=user, event=events[1])

    return msg1, msg2


@pytest.fixture
def user_messages(user: "User") -> "list[UserMessage]":
    """User messages fixture for filtering tests."""
    from testutils.factories import UserMessageFactory

    return [
        UserMessageFactory.create(user=user, displayed=None, read=None),  # new
        UserMessageFactory.create(user=user, displayed=True, read=None),  # unread
        UserMessageFactory.create(user=user, read=timezone.now()),  # read
    ]


@pytest.fixture
def same_app_event(user: "User"):
    from testutils.factories import EventFactory, UserMessageFactory

    event1 = EventFactory()
    event2 = EventFactory(application=event1.application)
    msg1 = UserMessageFactory(user=user, event=event1)
    UserMessageFactory(user=user, event=event2)

    return event1, event2, msg1


@pytest.fixture
def diff_app_event(user: "User"):
    from testutils.factories import EventFactory, UserMessageFactory

    event1 = EventFactory()
    event2 = EventFactory()
    msg1 = UserMessageFactory(user=user, event=event1)
    UserMessageFactory(user=user, event=event2)

    return event1, event2, msg1


@pytest.fixture
def app():
    from testutils.factories import ApplicationFactory

    return ApplicationFactory()


@pytest.mark.django_db
def test_console_index(django_app, message: "UserMessage") -> None:
    url: str = reverse("console:index")
    # First view: should be 'new'
    res = django_app.get(url, user=message.user)
    assert res.pyquery("span:contains('New')")

    # Second view: should no longer be 'new' but 'not read'
    res = django_app.get(url, user=message.user)
    assert not res.pyquery("span:contains('New')")
    assert res.pyquery("span:contains('Not Read')")


@pytest.mark.django_db
def test_console_detail(django_app, message: "UserMessage") -> None:
    # Ensure starting state is unread
    message.refresh_from_db()
    assert message.read is None

    url: str = reverse("console:detail", args=[message.pk])
    res = django_app.get(url, user=message.user)
    assert res.pyquery(f"div:contains('{message.subject}')")

    # Reload from database to verify side effect of viewing detail
    message.refresh_from_db()
    assert message.read is not None


@pytest.mark.django_db
def test_console_detail_already_read(django_app, message: "UserMessage") -> None:
    from django.utils import timezone

    message.read = timezone.now()
    message.save()

    url: str = reverse("console:detail", args=[message.pk])
    res = django_app.get(url, user=message.user)
    assert res.status_code == 200


@pytest.mark.django_db
def test_console_prefs(django_app, user) -> None:
    url: str = reverse("console:prefs")
    res = django_app.get(url, user=user)
    assert res.status_code == 200

    form = res.forms["user-preferences-form"]
    form["timezone"] = "Europe/Rome"
    res = form.submit()
    assert res.status_code == 302
    user.refresh_from_db()
    assert str(user.timezone) == "Europe/Rome"


@pytest.mark.parametrize("status", ["unread", "read", "all"])
def test_pwa_index_filtering(django_app, user: "User", user_messages: "list[UserMessage]", status: str) -> None:
    django_app.set_user(user)
    response = django_app.get(reverse("console:index") + f"?status={status}")
    assert response.status_code == 200
    messages = response.context["messages"]
    if status == "unread":
        assert all(m.instance.read is None for m in messages)
    elif status == "read":
        assert all(m.instance.read is not None for m in messages)


@pytest.mark.django_db
def test_console_index_filter_by_application(django_app, user: "User", diff_app_event) -> None:
    event1, event2, msg1 = diff_app_event

    django_app.set_user(user)
    response = django_app.get(reverse("console:index") + f"?application={msg1.event.application.pk}")
    assert response.status_code == 200
    messages = [f.instance for f in response.context["user_messages"]]
    assert len(messages) == 1
    assert messages[0].pk == msg1.pk


@pytest.mark.django_db
def test_console_index_filter_by_application_no_messages(django_app, user: "User", app: "Application") -> None:
    django_app.set_user(user)
    response = django_app.get(reverse("console:index") + f"?application={app.pk}")
    assert response.status_code == 200
    messages = [f.instance for f in response.context["user_messages"]]
    assert len(messages) == 0


@pytest.mark.django_db
def test_console_index_filter_by_event(
    django_app, user: "User", same_app_event: "tuple[Event, Event, UserMessage]"
) -> None:
    event1, event2, msg1 = same_app_event

    django_app.set_user(user)
    response = django_app.get(reverse("console:index") + f"?event={msg1.event.pk}")
    assert response.status_code == 200
    messages = [f.instance for f in response.context["user_messages"]]
    assert len(messages) == 1
    assert messages[0].pk == msg1.pk


@pytest.mark.django_db
def test_console_index_applications_context(django_app, user: "User", diff_app_event) -> None:
    event1, event2, _ = diff_app_event
    django_app.set_user(user)
    response = django_app.get(reverse("console:index"))
    assert response.status_code == 200
    apps = list(response.context["applications"])
    assert event1.application in apps
    assert event2.application in apps
