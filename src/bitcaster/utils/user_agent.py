import hashlib
from typing import TYPE_CHECKING

from django.conf import settings
from django.core.cache import BaseCache, caches
from user_agents.parsers import UserAgent

if TYPE_CHECKING:
    from bitcaster.types.http import AnyRequest

USER_AGENTS_CACHE = getattr(settings, "USER_AGENTS_CACHE", "default")
cache: BaseCache | None

if USER_AGENTS_CACHE:
    cache = caches[USER_AGENTS_CACHE]
else:  # pragma: no-cover
    cache = None


class SmartUserAgent(UserAgent):
    @property
    def is_ios(self) -> bool:
        return "iOS" in self.os.family

    @property
    def support_firebase(self) -> bool:
        return not ("iOS" in self.os.family or "Safari" in self.browser.family)

    @property
    def is_safari(self) -> bool:
        return "Safari" in self.browser.family


def parse(user_agent_string: str) -> SmartUserAgent:
    return SmartUserAgent(user_agent_string)


def get_cache_key(ua_string: bytes | str) -> str:
    # Some user agent strings are longer than 250 characters so we use its MD5
    if isinstance(ua_string, str):
        ua_string = ua_string.encode("utf-8")
    hasher = hashlib.new("sha256")
    hasher.update(ua_string)
    return f"django_user_agents.{hasher.hexdigest()}"


def get_user_agent(request: "AnyRequest") -> UserAgent:
    """Try to get UserAgent objects from cache before constructing a UserAgent from scratch.

    Because parsing regexes.yaml/json (ua-parser) is slow
    if not hasattr(request, 'META'):
        return None
    """
    ua_string = request.META.get("HTTP_USER_AGENT", "")
    if not ua_string:
        return UserAgent("")

    if not isinstance(ua_string, str):
        ua_string = ua_string.decode("utf-8", "ignore")

    if cache:
        key = get_cache_key(ua_string)
        user_agent = cache.get(key)
        if user_agent is None:
            user_agent = parse(ua_string)
            cache.set(key, user_agent)
    else:
        user_agent = parse(ua_string)
    return user_agent
