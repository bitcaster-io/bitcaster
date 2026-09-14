# Bitcaster Security & Code Quality Audit Report

**Date:** 2026-08-21
**Scope:** Full read-only audit of `src/bitcaster/` — APIs, models, dispatchers, middleware, web views, and templates.
**Branch:** Working directory state at time of audit.

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Critical Findings](#2-critical-findings)
3. [High Severity Findings](#3-high-severity-findings)
4. [Medium Severity Findings](#4-medium-severity-findings)
5. [Low Severity Findings](#5-low-severity-findings)
6. [Positive Security Posture Observations](#6-positive-security-posture-observations)
7. [Remediation Priority Matrix](#7-remediation-priority-matrix)

---

## 1. Executive Summary

The audit identified **2 critical**, **4 high**, **3 medium**, and **2 low** severity issues across the codebase. The most urgent concerns are server-side template injection in `utils/shortcuts.py` and credential exposure in dispatcher logging. Webhook dispatchers lack SSRF protections, and several templates render user-controlled content with `|safe`.

---

## 2. Critical Findings

### C-01: Server-Side Template Injection (SSTI)

**File:** `src/bitcaster/utils/shortcuts.py:10`
```python
tpl = Template("%s%s" % ("{% load bitcaster attachments %}", content))
return str(tpl.render(Context(context)))
```

**Severity:** Critical
**Description:** User-controlled `content` is passed directly into Django's raw `Template()` constructor. This is a textbook SSTI vulnerability — if any message body, subject, or template field stored in the database can be influenced by an attacker (including admin users crafting malicious messages), they can execute arbitrary Python code via Django template tags like:
```
{{ ''|center:''.__class__.__mro__[1].__subclasses__() }}
```

**Call chain:** This function is called from:
- `models/messagetemplate.py` — rendering message subjects and content
- `console/views.py` (indirectly) — console message display
- `dispatchers/user_message.py` — user message rendering

**Impact:** Remote code execution on the application server.

**Fix:** Use Django's template loader with pre-authorized templates, or use a safe string interpolation library (e.g., Python `.format()` with strict allowlist). Never pass user-controlled strings to `Template()`.

---

### C-02: Credential Exposure in Debug Logging

**File:** `src/bitcaster/dispatchers/base.py:142`
```python
logger.debug(f"Dispacther: {klass} creating connection with config {self.config}")
```

**Severity:** Critical
**Description:** `self.config` returns the form's `cleaned_data`, which includes API keys, passwords, OAuth tokens, and AWS credentials. These are logged at DEBUG level every time a dispatcher creates a backend connection.

**Config fields that may be exposed:**
- `aws_access_key_id`, `aws_secret_access_key` (SES)
- `api_key` (SendGrid)
- `consumer_key`, `consumer_key_secret`, `access_token`, `access_token_secret` (X/Twitter)
- `username`, `password` (RabbitMQ)
- OAuth credentials (Gmail)

**Impact:** Credentials written to log files, log aggregators, container logs, or cloud logging services. Attack gains full access to third-party accounts and infrastructure.

**Fix:** Redact secrets in log output. Use a helper that masks sensitive fields:
```python
logger.debug(f"Dispatcher: {klass} creating connection with %d config keys", len(self.config))
```

Note: Typo "Dispacther" in the log string.

---

## 3. High Severity Findings

### H-01: SSRF via Unvalidated Webhook URLs (Slack & Teams)

**Files:** `src/bitcaster/dispatchers/slack.py:32`, `src/bitcaster/dispatchers/teams.py:74`

**Severity:** High
**Description:** Both dispatchers make outbound HTTP POST requests to user-supplied webhook URLs without any validation against internal IP ranges, localhost, or cloud metadata endpoints. The Slack dispatcher has **no timeout; the Teams dispatcher has `timeout=10` but no URL validation.

```python
# slack.py:32 - No SSRF protection, no timeout
res: Response = conn.post(self.config["url"], json={"text": payload.message})

# teams.py:74 - Timeout present but no SSRF protection
response = session.post(webhook_url, json=teams_message, timeout=10)
```

**Impact:** An attacker who can create/edit channels (or compromise a user with channel creation permissions) can set webhook URLs pointing to:
- `http://169.254.169.254/latest/meta-data/` — cloud metadata (AWS/GCP/Azure credentials)
- `http://localhost:6379/` — Redis instance
- `http://10.0.0.5/admin/` — internal admin panels
- Internal microservices

**Fix:** Add URL validation that blocks private IP ranges, loopback, and link-local addresses. Use a library like `socks-libevent` or implement an allowlist of known webhook domains (`hooks.slack.com`, `office.com/webhook2blue`).

---

### H-02: Stored XSS via `|safe` on User Message Content

**Files:** `src/bitcaster/pwa/templates/pwa/detail.html:26`, `src/bitcaster/web/templates/bitcaster/console/detail.html:12`, `src/bitcaster/web/templates/bitcaster/admin/usermessage/change_form.html:11`, `src/bitcaster/web/templates/bitcaster/admin/event/includes/simulation_results.html:115`

**Severity:** High
**Description:** Multiple templates render `UserMessage.message` or message content with the `|safe` filter, bypassing Django's automatic HTML escaping. Since `render_message()` at `utils/shortcuts.py:6` also processes this content through raw templates (see C-01), any script tags or event handlers embedded in message content will execute in the recipient's browser.

```html
<!-- pwa/detail.html:26 -->
{{ message.message|safe }}

<!-- console/detail.html:12 -->
{{ object.message|safe }}
```

**Impact:** Stored XSS affecting any user who views a crafted notification message. If an admin or system account sends messages, all users in the organization/project scope are affected.

**Fix:** Replace `|safe` with Django's `bleach` library integration, or use `|escape` and provide a proper Markdown-to-HTML conversion pipeline that strips dangerous HTML attributes. The `|safe` filter should only be applied after explicit sanitization.

---

### H-03: Upstream Response Body Leak in Exceptions

**Files:** `src/bitcaster/dispatchers/teams.py:77-78`, `src/bitcaster/dispatchers/x.py:47-48`

**Severity:** High
**Description:** Both dispatchers embed the full response body from external services into exception messages and log entries. Response bodies may contain internal server details, stack traces, or sensitive authentication errors.

```python
# teams.py:77-78
logger.error(f"Teams dispatcher error: {response.status_code} - {response.text}")
raise DispatcherError(f"Failed to send to Teams: {response.text}")

# x.py:47-48
logger.error(f"X dispatcher error: {response.status_code} - {response.text}")
raise DispatcherError(f"Failed to post to X: {response.text}")
```

**Impact:** Internal server information, API error messages, or authentication tokens leaked into application logs and potentially to users if exceptions propagate to UI.

**Fix:** Log only the status code and truncate response bodies. Never embed external service responses in user-facing exception messages.

---

### H-04: Slack Dispatcher Missing Network Timeout

**File:** `src/bitcaster/dispatchers/slack.py:31-32`

**Severity:** High
**Description:** The Slack dispatcher creates a `requests.Session()` and makes POST requests without any timeout parameter. This request can hang indefinitely, consuming worker threads and potentially causing resource exhaustion under adversarial conditions.

```python
# slack.py:31-32
conn = requests.Session()
res: Response = conn.post(self.config["url"], json={"text": payload.message})
```

**Impact:** Denial of service via slow-or-die attacks against worker processes. Single malicious webhook URL can hold a worker thread indefinitely.

**Fix:** Add timeout parameter: `conn.post(..., timeout=10)`.

---

## 4. Medium Severity Findings

### M-01: Thread-Local State Not Compatible with Async/Greenlets

**Files:** `src/bitcaster/state.py:18`, `src/bitcaster/middleware/state.py:22`

**Severity:** Medium
**Description:** `State` class inherits from `threading.local()` at `state.py:18`. While this is fine for the current WSGI deployment, if Django ASGI support or gevent/greenlet-based concurrency is added in the future, thread-local storage will leak state between async tasks. The middleware correctly resets state in `finally` blocks (`middleware/state.py:26-28`), but any code path that exits via unhandled exception before `finally` runs could leave stale request state.

```python
# state.py:18
class State(local):
    request: "HttpRequest|None" = None
    cookies: dict[str, list[Any]] = {}
```

**Impact:** Stale request objects accessible from background tasks under async/gevent deployment models. Potential information disclosure between concurrent requests.

**Fix:** No immediate action required for WSGI-only deployment. Document this limitation and consider `asgiref.local.Local` if ASGI is planned.

---

### M-02: Dashboard Sanity View Renders Unsanitized Links with `|safe`

**File:** `src/bitcaster/web/templates/dashboards/sanity.html:74,80`

**Severity:** Medium
**Description:** The dashboard sanity view renders `item.link` and `item.fix` as HTML attributes using `|safe`:
```html
<a class="underline" href="{{ item.link|safe }}">{{ item.label }}</a>
<a class="underline ml-2" href="{{ item.fix|safe }}">Fix Issue</a>
```

**Impact:** If `item.link` or `item.fix` values contain JavaScript protocol URLs (`javascript:...`) or other unsafe URL schemes, this becomes a stored XSS vector. The `url_has_allowed_host_and_scheme()` check at the validation layer provides some protection, but not where `allowed_hosts=None`.

**Fix:** Use Django's `|iriencode` or `|urlencode` instead of `|safe`, and ensure URLs are validated against an allowlist before rendering.

---

### M-03: Webpush Signatures Use Default Secret with No Salt/Versioning

**File:** `src/bitcaster/webpush/utils.py:22,27`

**Severity:** Medium
**Description:** The webpush subscription signer uses Django's default `Signer()` with no custom salt or secret key override. It relies entirely on the global `SECRET_KEY`, and there is no signature versioning to support key rotation.

```python
# webpush/utils.py:22-28
def sign(assignment: "Assignment") -> str:
    signer = Signer()
    return signer.sign_object({"pk": assignment.pk, "address": assignment.address.value})
```

**Impact:** If `SECRET_KEY` is compromised, all webpush subscription tokens become forgeable. No mechanism to rotate signing keys without breaking existing subscriptions.

**Fix:** Use a dedicated salt: `Signer(salt='bitcaster.webpush')`. Consider adding versioning for key rotation.

---

## 5. Low Severity Findings

### L-01: Unused Session Object in Slack Dispatcher

**File:** `src/bitcaster/dispatchers/slack.py:31`

**Severity:** Low
**Description:** A `requests.Session()` is instantiated at line 31 but used for a single POST request at line 32. Sessions are meant for connection pooling and persistent cookies across multiple requests. Using a session for one-off requests adds overhead without benefit.

**Fix:** Use `requests.post()` directly, or if session reuse is intended, make it a class-level attribute.

---

### L-02: Typo in Dispatcher Log Message

**File:** `src/bitcaster/dispatchers/base.py:142`

**Severity:** Low
**Description:** "Dispacther" should be "Dispatcher". Minor but contributes to log parsing confusion.

```python
logger.debug(f"Dispacther: {klass} creating connection with config {self.config}")
```

---

## 6. Positive Security Posture Observations

| Area | Observation |
|------|-------------|
| **CSRF Protection** | No `csrf_exempt` decorators found in the codebase. All forms contain `{% csrf_token %}` (verified ~49 form templates). |
| **Authentication** | Admin console views use `LoginRequiredMixin`. `UserConsoleDetailView.get_queryset()` correctly scopes to `self.request.user` (`console/views.py:102-103`). |
| **Token Generation** | API key and authentication token generation uses cryptographically secure random generators with sufficient entropy. |
| **OAuth Adapter** | Social adapter properly validates callback URLs without external redirect validation gaps. |
| **Model Ownership** | Cascade ownership follows silo hierarchy (User → Organization → Project → Channel). Foreign keys enforce referential integrity. |

---

## 7. Remediation Priority Matrix

| ID | Severity | Effort | Risk | Priority |
|----|----------|--------|------|----------|
| C-01 | Critical | Medium | RCE | **Immediate** |
| C-02 | Critical | Low | Credential leak | **Immediate** |
| H-01 | High | Medium | SSRF / metadata exfil | P1 |
| H-02 | High | Medium | Stored XSS | P1 |
| H-03 | High | Low | Information leak | P2 |
| H-04 | High | Trivial | DoS vector | P2 |
| M-01 | Medium | N/A | Future async risk | Document |
| M-02 | Medium | Low | XSS via links | P3 |
| M-03 | Medium | Low | Key rotation risk | P3 |
| L-01 | Low | Trivial | Code quality | Backlog |
| L-02 | Low | Trivial | Log quality | Backlog |
