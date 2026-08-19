# Project Code Conventions

This document collects the code conventions of the Bitcaster codebase. Each rule states the requirement and the concrete pattern observed in the code. Follow these when writing code.

## Django Models

- **Field attributes order**: within a field definition, attributes must appear in this exact order:
  `verbose_name`, `on_delete`, `to`, `related_name`, `max_length`, `upload_to`, `choices`, `blank`, `null`, `default`, `db_index`, `db_collation`, `unique`, `editable`, `auto_now`, `auto_now_add`, `chained_field`, `chained_model_field`, other custom args, `validators`, `help_text`.
  - Exception: for `ForeignKey`, `to` and `on_delete` may precede `verbose_name`.
  - Exception: `ChoiceArrayField` may start with `base_field`.
- **`verbose_name` and `help_text` are mandatory on every field** and MUST be wrapped with gettext `_("...")`. Use `gettext_lazy as _` in model bodies.
- **`choices` must be a callable**: pass `choices=SomeTextChoices.choices` (inner/external `TextChoices`/`IntegerChoices` class) or a `def get_xxx_choices() -> list[tuple]` function — never a literal list/tuple/constant on the field.
- **Inherit `BitcasterBaseModel`** (provides `version` `IntegerVersionField`, `created` `auto_now_add`, `last_updated` `auto_now`) unless the model has specific needs (`AdminReversable` alone for `Monitor`).
- **Use the provided mixins** instead of re-implementing: `SlugMixin` (name+slug+`__str__`), `LockMixin` (locked/paused + lock/unlock/pause/resume), `Scoped2Mixin`/`Scoped3Mixin` (org→project→application auto-resolve on `save()` and `clean()`).
- **No UUID PKs** — use default `BigAutoField` id + `natural_key()` / `get_by_natural_key()` for cross-model identity.
- **Managers**: one custom manager per model (subclassing `BitcasterBaselManager`), always named `objects`; use `from_queryset` for models needing custom queryset methods; use `ScopedManager` for models with scoped FKs; use `.local()` (not `.objects`) to exclude system-org objects when querying user-facing data.
- **Meta**: always set `_()`-wrapped `verbose_name`/`verbose_name_plural`; `ordering = ("name",)` as default; `unique_together`/named `UniqueConstraint` for parent-scoped uniqueness; named `Index` for hot query paths; `app_label = "bitcaster"` for models defined outside the main app.
- **`save()` overrides** for derived data: owner fallback up the hierarchy (`try: self.owner except User.DoesNotExist: self.owner = self.project.owner`), slugify, protocol-from-dispatcher. See `.ai/domain.md` for the ownership cascade.

## Admin

- **All admins inherit `BaseAdmin[Model]`** (which itself composes `BitcasterModelAdmin(UnfoldModelAdmin)` + filters/extra-buttons mixins). One file per model: `admin/<model>.py` with class `{Model}Admin`.
- **Every `ForeignKey` displayed in the admin MUST be in `autocomplete_fields`** — unless it is in `readonly_fields` or a radio field.
- **Never expose sensitive fields in `list_display`**: `secret`, `key`, `password`, `token`, `api_key`, `client_secret`, `private_key`, `access_token`, `refresh_token`, `auth_token`, `secret_key`. Reveal secrets only via dedicated button views (e.g. `show_key` with expiry + permission gating), and use `get_exclude` to keep them out of forms.
- **fieldsets use Unfold tabs**: `{"classes": ["tab"], "fields": [...]}` with `gettext_lazy` titles; separate `add_fieldsets` for the create form.
- **Derived/display columns**: trailing underscore for scalar methods (`dispatcher_`, `agent_`), `_badge`/`_link` suffix with `unfold.decorators.display` for badges, `@display(boolean=True)` for booleans.
- **`get_queryset` must `select_related`** FK chains; reuse via `list_select_related`.
- **System-org protection**: `get_readonly_fields`/`has_*_permission` guards for records owned by the protected `bitcaster` org (see `.ai/domain.md`).
- **Dynamic initial data** via `get_changeform_initial_data` (owner/user from `request.user`, relations from GET params/cookies).
- **Actions**: boolean toggles via shared `admin_toggle_bool_action` helper; destructive flows via `confirm_action`; `admin_extra_buttons` decorators (`@button`, `@link`, `@view`, `@choice`) with `ButtonColor` enums.

## Dispatchers

- **Inherit `Dispatcher`**, define `slug`, `verbose_name`, `config_class` (a `forms.Form` subclass named `{Name}Config`), `protocol` (`MessageProtocol`), and optional `backend`.
- **Every `send` implementation MUST wrap delivery logic in `try...except Exception` raising only `DispatcherError(...) from e`**. The base `Dispatcher.send()` wrapper enforces this; subclass `_send` and let the base wrap, or wrap explicitly.
- Access validated configuration via `self.config["key"]` (form-validated, raises `ValidationError` on bad config). Never log secrets; use `logger.exception(e)` then re-raise.
- Full template, config validation, and testing requirements: see `.ai/dispatchers.md`.

## Background Tasks (Dramatiq / runner)

- **Every actor MUST use `@dramatiq.actor(actor_class=SmartActor, ...)`**.
- **Actor names must stay short** — keep function names under 1000 characters.
- Use `logging=True` for actors needing `ProcessLogEntry` audit; `max_retries=0` for batch/purge/simulation tasks where retries are harmful.
- **Enqueue with `.send()`, never `.delay()`**; pass primitive PKs (never ORM objects); re-fetch the object inside the task with `select_related`.
- **Lazy-import Django models inside task bodies**, never at module top.
- Error handling: per-item `try/except` with `logger.exception(e)` and continue; catch→record-state→re-raise only when retries should run.
- Recurring jobs go through APScheduler via the `SCHEDULER` dict in `runner/config.py`.
- All external calls / heavy processing MUST be offloaded to tasks — never in the request-response cycle (see `.ai/standards.md`).

## Migrations

- **Indexes must be added concurrently**: use `django.contrib.postgres.operations.AddIndexConcurrently`, never `migrations.AddIndex`.

## Type Annotations

- **Modern syntax only** (Python 3.13):
  - `X | Y` not `Union[X, Y]`; `X | None` not `Optional[X]`
  - `list[X]`, `dict[K, V]`, `tuple[X, ...]`, `type[X]` — never `List`/`Dict`/`Tuple`/`Type`
- Mandatory type hints on all new functions (`django-stubs` patterns); classes are generic over their model (`class XAdmin(BaseAdmin[X])`, `ModelSerializer[M]`, `ModelForm[M]`); `TYPE_CHECKING` guards for typing-only imports.

## Imports

- **Relative imports within `src/bitcaster/`**, never absolute `bitcaster.*` imports inside the package.
- **Relative imports may go up at most 2 levels**; beyond that use absolute imports from the top-level package.
- isort sections (django, testing, typing, first-party) are configured in `ruff.toml` — `tox -e lint` fixes ordering.

## Testing

- **Never call Factory classes directly in test bodies**: define fixtures that wrap factories (`UserFactory.create()` inside a fixture) and import factories lazily inside the fixture. See `.ai/testing-patterns.md`.
- Test files mirror `src/` structure; prefixes: `test_d_*` dispatchers, `test_p_*` webpush, `test_f_*` selenium, `test_model_*` models; module-level `pytestmark` lists with `pytest.mark.django_db` etc.
- HTTP mocking via `mocked_responses` fixture (YAML fixture replay for mailjet); low-level libs via `patch(..., autospec=True)`; freezegun for time-based scenarios.
- Assert with debug context: `assert res.status_code == ..., res.json()`.

## Logging

- Module-level `logger = logging.getLogger(__name__)` in every module; never `print()`.
- **Never put exception objects in a logger's `extra` dict** — it can pin thread references (Sentry + asgiref memory leak). Use `str(exc)` or `logger.exception(e)`.
- `logger.exception(e)` in `except` blocks before handling; `logger.debug` per-item detail, `logger.info` phase summaries, `logger.warning` for recoverable issues (lazy `%s` formatting).

## API (DRF)

- Compose `SecurityMixin` (auth + `ApiApplicationPermission` + grants + throttling + exception handling) — never re-declare DRF defaults.
- Declare `required_grants = [Grant.X]` on every view; use `@extend_schema` with lazy `_()` descriptions on every handler.
- Serializers: explicit `fields` tuples, `SerializerMethodField` for derived/nested data, `source=` + `read_only=True` for flattening, per-action serializers via `action_serializers` + `get_serializer_class`.
- Catch domain exceptions at the view boundary and translate to proper HTTP status with `{"error": str(e)}` payloads — never let domain errors escape as 500s.

## Error Handling

- Domain exceptions live in `bitcaster/exceptions.py`; raise with context: `raise XError(...) from e` inside `except` blocks; `raise forms.ValidationError(...) from None` when wrapping lower-level validation.
- Business logic lives on models/managers (fat models) with `TypedDict` option contracts; `handlers.py` files are for Django signal wiring only.
- Filtering/payload rules must pass the shared validators (`validate_schema`, `validate_filters`, `validate_lookups` in `utils/filtering.py`) before being persisted.
