# API Development Guide

## Throttling

Bitcaster uses a sliding window algorithm for API rate limiting, implemented in `SlidingWindowThrottle`. This mechanism ensures a smoother rate limit compared to fixed window counters and is backed by Redis for atomicity.

### Customising Thresholds

You can customise the rate limit (number of requests) and the window (duration in seconds) at different levels. The system resolves these values with the following priority:

#### 1. Per-Action (Directly on Method)
This is the most granular way to define limits, especially useful for methods decorated with `@action`.

```python
@action(detail=True, methods=["post"])
def trigger(self, request, pk=None):
    ...
trigger.throttle_rate = 5
trigger.throttle_window = 60
```

#### 2. Per-Action (On ViewSet Class)
You can also define action-specific limits as class attributes using the `throttle_rate_{action_name}` and `throttle_window_{action_name}` naming convention.

```python
class EventViewSet(viewsets.ViewSet):
    throttle_rate_list = 100
    throttle_window_list = 3600
```

#### 3. View-Level Default
If no action-specific override is found, the ViewSet will fall back to its own defaults.

```python
class EventViewSet(viewsets.ViewSet):
    throttle_rate = 50
    throttle_window = 60
```

#### 4. Global Default
If none of the above are defined, the defaults from the `SlidingWindowThrottle` class are used (default: 30 requests per 60 seconds).

## Implementation Details

The implementation can be found in `src/bitcaster/api/throttling.py`. It uses a LUA script to perform the "check-and-add" operation atomically in Redis.

An in-memory fallback mechanism is provided in case the Redis connection fails, ensuring the system remains operational though with slightly less precise rate limiting across multiple application instances.
