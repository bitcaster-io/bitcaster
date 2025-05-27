# CSP_DEFAULT_SRC = ["'self'", "'unsafe-inline'", "'same-origin'", "fonts.googleapis.com", 'fonts.gstatic.com', 'data:',
#                    'blob:', "cdn.redoc.ly"]
# CSP_DEFAULT_SRC = ["'self'", "'unsafe-inline'", "'unsafe-eval'"]
# CSP_STYLE_SRC = ["'self'", "'unsafe-inline'", "same-origin", "fonts.googleapis.com", "fonts.gstatic.com"]
# CSP_SCRIPT_SRC = ["'self'", "'unsafe-inline'", "same-origin", "blob:", "'unsafe-eval'"]
# CSP_IMG_SRC = ["'self'", "'unsafe-inline'", "same-origin", "blob:", "data:", "cdn.redoc.ly"]
# CSP_FONT_SRC = ["'self'", "fonts.googleapis.com", "same-origin", "fonts.googleapis.com", "fonts.gstatic.com", "blob:"]

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
        ],
        "img-src": ["'self'", "'unsafe-inline'", "same-origin", "blob:", "data:", "cdn.redoc.ly"],
        "script-src": ["'self'", "'unsafe-inline'", "same-origin", "blob:", "'unsafe-eval'"],
        "style-src": ["'self'", "'unsafe-inline'", "same-origin", "fonts.googleapis.com", "fonts.gstatic.com"],
    }
}
