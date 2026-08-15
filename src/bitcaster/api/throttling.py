from typing import Any

import time
import uuid

from rest_framework.request import Request
from rest_framework.throttling import BaseThrottle
from rest_framework.views import APIView

from django.core.cache import cache, caches

from bitcaster.models import ApiKey, ClientToken

# Rate limiting with Sliding Window using LUA for atomicity
LUA_SLIDING_WINDOW = """
local key = KEYS[1]
local now = tonumber(ARGV[1])
local window_size = tonumber(ARGV[2])
local max_requests = tonumber(ARGV[3])
local member_id = ARGV[4]

-- 1. Remove requests older than the time window
redis.call('ZREMRANGEBYSCORE', key, 0, now - window_size)

-- 2. Count remaining requests
local current_count = redis.call('ZCARD', key)

-- 3. If under limit, add the current request
if current_count < max_requests then
    redis.call('ZADD', key, now, member_id)
    return 1
else
    return 0
end
"""


class SlidingWindowThrottle(BaseThrottle):
    """
    Throttling implementation using a sliding window algorithm.

    Thresholds can be customised:
    1. Directly on the @action method
        ```
        @action(detail=True)
        def my_action(self, request, pk=None):
            ...
        my_action.throttle_rate = 5
        ```
    2. On the ViewSet class using throttle_rate_{action_name}
        ```
        class MyViewSet(ViewSet):
            throttle_rate_my_action = 5
        ```
    3. On the View class using throttle_rate
        ```
        class MyViewSet(ViewSet):
            throttle_rate = 10
        ```
    """

    rate: int = 30
    window: int = 60  # seconds

    def _get_attr(self, view: Any, attr_name: str, default: int) -> int:
        action_name: str | None = getattr(view, "action", None)
        if action_name:
            # 1. Check if defined directly on the method (useful for @action)
            action_method = getattr(view, action_name, None)
            val = getattr(action_method, attr_name, None)
            if val is not None:
                return int(val)

            # 2. Check for class-level override with suffix (e.g., throttle_rate_create)
            val = getattr(view, f"{attr_name}_{action_name}", None)
            if val is not None:
                return int(val)

        # 3. Check for generic class-level override (e.g., throttle_rate)
        # 4. Fallback to default
        return int(getattr(view, attr_name, default))

    def get_rate(self, view: Any) -> int:
        return self._get_attr(view, "throttle_rate", self.rate)

    def get_window(self, view: Any) -> int:
        return self._get_attr(view, "throttle_window", self.window)

    def allow_request(self, request: Request, view: APIView) -> bool:
        auth = getattr(request, "auth", None)
        if auth:
            if isinstance(auth, ClientToken) or (isinstance(auth, ApiKey) and auth.is_web()):
                key = f"throttle_{type(auth).__name__}_{auth.id}_{self.get_ident(request)}"
            else:
                key = f"throttle_{auth.id}"
        elif request.user.is_authenticated:
            key = f"throttle_{request.user.id}"
        else:
            key = f"throttle_ip_{self.get_ident(request)}"

        now: float = time.time()
        member_id: str = f"{now}_{uuid.uuid4()}"
        rate: int = self.get_rate(view)
        window: int = self.get_window(view)

        try:
            redis_client = caches["default"].client.get_client()
            allowed = redis_client.eval(LUA_SLIDING_WINDOW, 1, key, now, window, rate, member_id)
            return bool(allowed)
        except Exception:
            return self.in_memory_fallback(key, rate, window)

    def in_memory_fallback(self, key: str, rate: int, window: int) -> bool:
        fallback_key: str = f"fallback_{key}"
        count: int = cache.get(fallback_key, 0)
        if count < rate:
            cache.set(fallback_key, count + 1, window)
            return True
        return False

    def wait(self) -> float:
        return self.window / self.rate
