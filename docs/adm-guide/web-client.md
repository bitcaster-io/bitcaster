# Trigger Events from a Web Page

Bitcaster can be triggered directly from a web page (browser JavaScript).
Because browser code is visible to any visitor, static API keys must never be
embedded in pages. Bitcaster provides two safe mechanisms for browser clients:

1. **Web API Keys** — hardened, origin-bound, trigger-only keys that *can*
   live in a page.
2. **Client Tokens** — very short-lived tokens minted by your backend through
   the token exchange endpoint; the static key never leaves your server.

Both mechanisms share the same properties:

- scoped to a single application;
- restricted to triggering events (no reads, no writes, no auto-create);
- bound to an explicit list of allowed origins: requests without a matching
  `Origin` header are rejected;
- expiring and individually revocable;
- throttled per key and client IP.

## 1. Web API Keys

Create an API key with:

- **Kind**: `Web Key`
- **Grant**: `Web Event Trigger` only
- **Scope**: an application (required)
- **Allowed origins**: the origins of the pages that will use the key
- **Expires at**: optional but recommended

Then trigger events from the page:

```javascript
fetch("https://bitcaster.example.com/api/o/{org}/p/{prj}/a/{app}/e/{event}/trigger/", {
    method: "POST",
    headers: {
        "Authorization": "Key <WEB_API_KEY>",
        "Content-Type": "application/json",
    },
    body: JSON.stringify({ context: { "key": "value" } }),
});
```

A web key is rejected (403) when the request has no `Origin` header or an
origin outside the allowlist. This prevents other websites from reusing a key
found in your page.

## 2. Client Tokens (recommended for production)

The static key stays on your backend. The backend exchanges it for a short-lived
client token, which is then embedded in the page (or served to it) and used by
the browser.

**Mint a token** (server side, with a server API key that has `event:trigger`):

```bash
curl -X POST https://bitcaster.example.com/api/o/{org}/p/{prj}/a/{app}/token/ \
     -H "Authorization: Key <SERVER_API_KEY>" \
     -H "Content-Type: application/json" \
     -d '{
           "origin": "https://example.com",
           "event": "order-created"
         }'
```

- `origin` (required): the origin of the page that will use the token.
- `event` (optional): bind the token to a single event.

Response:

```json
{
    "token": "...",
    "expires_at": "2026-08-13T12:15:00Z",
    "event": "order-created"
}
```

The token lives for `CLIENT_TOKEN_TTL` seconds (default 900) and can only
trigger events. Use it from the browser like a key:

```javascript
fetch("https://bitcaster.example.com/api/o/{org}/p/{prj}/a/{app}/e/{event}/trigger/", {
    method: "POST",
    headers: { "Authorization": "Key <CLIENT_TOKEN>" },
    body: JSON.stringify({ context: {} }),
});
```

Revocation is immediate: disable the token in the admin, or rotate the parent
key. Expired tokens are removed by the `cleanup_client_tokens` management
command and lazily on each new mint.

## 3. Browser client library

The standalone `@bitcaster/js` package wraps both flows with a single API —
see its README for usage and examples.

## Configuration

| Setting | Default | Description |
| --- | --- | --- |
| `CORS_ALLOWED_ORIGINS` | `[]` | Origins allowed to call the API from a browser |
| `CLIENT_TOKEN_TTL` | `900` | Lifetime (seconds) of minted client tokens |
| `TRIGGER_CONTEXT_MAX_SIZE` | `32768` | Max size in bytes of the `context` payload from web credentials |
