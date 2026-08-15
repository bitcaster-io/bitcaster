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

---

## Adding a New Endpoint

All public endpoints live in `src/bitcaster/api/` and are wired in `src/bitcaster/api/urls.py`.

### 1. Create the View

Write a view class in `src/bitcaster/api/<resource>.py`. Every endpoint must:

- extend `SecurityMixin` (`src/bitcaster/api/base.py`), which provides the authentication classes (`ApiKeyAuthentication`, `BasicAuthentication`, `SessionAuthentication`), the permission class (`ApiApplicationPermission`) and the `SlidingWindowThrottle` throttle;
- declare `required_grants` with the grants the caller needs (see `src/bitcaster/auth/constants.py`, e.g. `Grant.ORGANIZATION_READ`, `Grant.EVENT_TRIGGER`, `Grant.MANAGE_APPLICATION_USERS`);
- set `serializer_class` (serializers live in `src/bitcaster/api/serializers.py`);
- decorate every handler with `@extend_schema(...)` so the OpenAPI schema stays complete.

```python
from bitcaster.api.base import SecurityMixin
from bitcaster.auth.constants import Grant

class MyResourceView(SecurityMixin, RetrieveAPIView):
    serializer_class = MyResourceSerializer
    required_grants = [Grant.ORGANIZATION_READ]
    lookup_url_kwarg = "slug"
    lookup_field = "slug"

    def get_queryset(self):
        return MyResource.objects.filter(organization__slug=self.kwargs["org"])

    @extend_schema(responses={200: MyResourceSerializer})
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
```

### 2. Register the URL

Add the path in `src/bitcaster/api/urls.py`. Routing conventions:

- `o/<slug:org>/` for organization-scoped resources;
- `o/<slug:org>/p/<slug:prj>/` for project-scoped resources;
- `o/<slug:org>/p/<slug:prj>/a/<slug:app>/` for application-scoped resources;
- `me/...` for the authenticated user profile.

```python
path(
    "o/<slug:org>/my-resource/<slug:slug>/",
    MyResourceView.as_view({"get": "retrieve"}),
    name="my-resource-detail",
),
```

### 3. Scope and Grant Enforcement

`ApiBasePermission` (`src/bitcaster/api/permissions.py`) validates that the API key's organization/project/application scope matches the URL kwargs and that the key's grants intersect the view's `required_grants`. A key with `FULL_ACCESS` bypasses the grant check. Out-of-scope keys or missing grants fail with `403` and an `InvalidGrantError` message.

### 4. Document the Endpoint

Add the endpoint to the API reference under `docs/api/` (one page per resource, e.g. `docs/api/users.md`) with the method, path, parameters, request/response examples and required grants.

### 5. Test It

Add integration tests under `tests/api/test_api_<resource>.py` following the existing patterns:

- fixtures with a valid API key (`tests/api/conftest.py`);
- happy path, missing grant (`403`), wrong scope, invalid payload (`4xx`) and idempotency cases;
- add the new URL to the public-URL list checked by `tests/api/test_api_smoke.py`;
- the schema tests (`tests/api/test_api_schema.py`) assert the OpenAPI schema and the Swagger/Redoc render — a missing `@extend_schema` breaks them.
