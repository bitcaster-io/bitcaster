# Trigger Events from a Web Page

Bitcaster can be triggered directly from a web page (browser JavaScript).
Because browser code is visible to any visitor, API keys must never be embedded
in pages. Instead, a **web API key** stays on your backend, which derives a
browser-safe *signing secret* from it. Pages use that secret to sign requests
with an HMAC-SHA256 signature that the Bitcaster API verifies.

The signed requests are:

- scoped to a single application;
- restricted to triggering events (no reads, no writes, no auto-create);
- bound to an explicit list of allowed origins: requests without a matching
  `Origin` header are rejected;
- validated against a timestamp skew window (see `HMAC_SIGNATURE_MAX_SKEW`);
- throttled per key and client IP.

## 1. Set up a web API key

Create an API key with:

- **Kind**: `Web Key`
- **Grant**: `Web Event Trigger` only
- **Scope**: an application (required)
- **Allowed origins**: the origins of the pages that will use the key
- **Expires at**: optional but recommended

The master key itself is only used server side. Derive the signing secret that
can be safely embedded in (or served to) the page:

```python
from bitcaster.models import ApiKey

key = ApiKey.objects.get(name="my-web-key")
secret = key.get_web_signing_secret()
```

The derived secret cannot be used as a bearer token and does not reveal the
master key: it only allows signing trigger requests.

## 2. Sign requests from the browser

Sign the request with an HMAC-SHA256 over the canonical representation:

```
METHOD\nPATH\nTIMESTAMP\nSHA256_HEX(BODY)
```

where:

- `METHOD` is the HTTP method, e.g. `POST`;
- `PATH` is the request path (no scheme, no host, no query string), e.g.
  `/api/o/{org}/p/{prj}/a/{app}/e/{event}/trigger/`;
- `TIMESTAMP` is the Unix timestamp (seconds) used in the `X-Timestamp` header;
- `SHA256_HEX(BODY)` is the hex-encoded SHA-256 digest of the raw request body.

Send two extra headers:

```
Authorization: HMAC-SHA256 <key_id>:<signature>
X-Timestamp: <unix timestamp in seconds>
```

where `key_id` is the first 16 characters of the master API key and
`signature` is the hex-encoded HMAC-SHA256 of the canonical string, keyed with
the derived signing secret. Requests whose timestamp differs from server time
by more than `HMAC_SIGNATURE_MAX_SKEW` seconds are rejected.

Example (web key; the `Origin` header must match the allowed origins):

```javascript
async function trigger(url, body) {
    const timestamp = Math.floor(Date.now() / 1000);
    const canonical = [
        "POST",
        new URL(url).pathname,
        timestamp,
        sha256Hex(JSON.stringify(body)),
    ].join("\n");
    const signature = hmacSha256Hex(SIGNING_SECRET, canonical);
    const res = await fetch(url, {
        method: "POST",
        headers: {
            "Authorization": `HMAC-SHA256 ${KEY_ID}:${signature}`,
            "X-Timestamp": String(timestamp),
            "Origin": window.location.origin,
            "Content-Type": "application/json",
        },
        body: JSON.stringify(body),
    });
    return res;
}
```

A request is rejected (403) when the `Origin` header is missing or not in the
key's allowed origins, and (401) when the signature or timestamp is invalid.

## 3. Browser client library

The standalone `@bitcaster/js` package wraps this flow with a single API —
see its README for usage and examples.

## Configuration

| Setting | Default | Description |
| --- | --- | --- |
| `CORS_ALLOWED_ORIGINS` | `[]` | Origins allowed to call the API from a browser |
| `HMAC_SIGNATURE_MAX_SKEW` | `300` | Max allowed skew (seconds) between `X-Timestamp` and server time |
| `TRIGGER_CONTEXT_MAX_SIZE` | `32768` | Max size in bytes of the `context` payload from web credentials |
