from bitcaster.config import env

# Explicit allowlist of origins allowed to call the API from a browser.
# Requests carrying an Origin header are only served CORS headers when the
# origin is listed here. Use full origins, e.g. "https://example.com".
CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS")
CORS_URLS_REGEX = r"^/api/.*$"
CORS_ALLOW_CREDENTIALS = False
CORS_ALLOW_METHODS = ("DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT")
CORS_ALLOW_HEADERS = ("accept", "authorization", "content-type", "x-requested-with")
CORS_PREFLIGHT_MAX_AGE = 86400
