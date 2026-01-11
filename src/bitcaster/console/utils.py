from datetime import datetime
from typing import TYPE_CHECKING

from django.db.models import Max

from bitcaster.cache.manager import CacheManager
from bitcaster.models import UserMessage

if TYPE_CHECKING:
    from bitcaster.models.user_message import UserMessageQuerySet


def set_user_latest_display_time(user_id: int, dm: CacheManager | None = None) -> datetime:
    if dm is None:
        dm = CacheManager(None)
    base_key = f"user_messages:{user_id}"
    with dm.activate_namespace(base_key):
        return dm.touch("seen")


def get_user_latest_display_time(user_id: int, dm: CacheManager | None = None) -> datetime:
    if dm is None:
        dm = CacheManager(None)
    base_key = f"user_messages:{user_id}"
    with dm.activate_namespace(base_key):
        return dm.get_last_touch("seen")


def set_user_latest_notify_time(user_id: int, dm: CacheManager | None = None) -> datetime:
    if dm is None:
        dm = CacheManager(None)
    base_key = f"user_messages:{user_id}"
    with dm.activate_namespace(base_key):
        return dm.touch("notify")


def get_user_latest_notify_time(user_id: int, dm: CacheManager | None = None) -> datetime:
    if dm is None:
        dm = CacheManager(None)
    base_key = f"user_messages:{user_id}"
    with dm.activate_namespace(base_key):
        return dm.get_last_touch("notify")


def get_users_to_notify() -> list[int]:
    from bitcaster.models import UserMessage

    qs = UserMessage.objects.filter(read__isnull=True).values("user_id").annotate(recent=Max("created"))
    user_to_notify = []
    for entry in qs.all():
        user_last_notify = get_user_latest_notify_time(entry["user_id"])
        if entry["recent"] > user_last_notify:
            user_to_notify.append(entry["user_id"])
    return list(set(user_to_notify))


def get_unseen_message_for_user(uid: int) -> "UserMessageQuerySet":
    last_seen = get_user_latest_display_time(uid)
    return UserMessage.objects.filter(read__isnull=True, created__gt=last_seen)  # type: ignore[return-value]
