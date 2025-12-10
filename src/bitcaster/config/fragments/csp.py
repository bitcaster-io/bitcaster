CONTENT_SECURITY_POLICY = {
    "DIRECTIVES": {
        "default-src": ["'self'", "'unsafe-inline'", "'unsafe-eval'"],
        "font-src": [
            "'self'",
            "fonts.googleapis.com",
            "same-origin",
            "fonts.googleapis.com",
            "fonts.gstatic.com",
            "blob:",
            "https://ajax.googleapis.com",
        ],
        "img-src": [
            "'self'",
            "'unsafe-inline'",
            "same-origin",
            "blob:",
            "data:",
            "cdn.redoc.ly",
        ],
        "script-src": [
            "'self'",
            "'unsafe-inline'",
            "same-origin",
            "blob:",
            "'unsafe-eval'",
        ],
        "script-src-elem": [
            "'self'",
            "'unsafe-inline'",
            "'unsafe-eval'",
            "same-origin",
            "blob:",
            "https://ajax.googleapis.com",
        ],
        "style-src": [
            "'self'",
            "'unsafe-inline'",
            "same-origin",
            "fonts.googleapis.com",
            "fonts.gstatic.com",
        ],
    }
}
