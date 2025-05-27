from typing import Any

from bitcaster import VERSION

REST_FRAMEWORK: dict[str, Any] = {
    # "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    # "DEFAULT_VERSIONING_CLASS": "rest_framework.versioning.NamespaceVersioning",
    # "DEFAULT_FILTER_BACKENDS": ("django_filters.rest_framework.DjangoFilterBackend",),
    # "DEFAULT_RENDERER_CLASSES": (
    #     "rest_framework.renderers.JSONRenderer",
    #     "rest_framework.renderers.BrowsableAPIRenderer",
    #     "rest_framework_datatables.renderers.DatatablesRenderer",
    # ),
    # "PAGE_SIZE": 30,
    "DEFAULT_AUTHENTICATION_CLASSES": [
        #     "rest_framework.authentication.BasicAuthentication",
        "rest_framework.authentication.SessionAuthentication",
        #     "rest_framework.authentication.TokenAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.DjangoModelPermissions",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

JWT_AUTH: dict[str, Any] = {
    # "JWT_VERIFY": False,  # this requires private key
    # "JWT_VERIFY_EXPIRATION": True,
    # "JWT_LEEWAY": 60,
    # "JWT_EXPIRATION_DELTA": datetime.timedelta(seconds=30000),
    # "JWT_AUDIENCE": None,
    # "JWT_ISSUER": None,
    # "JWT_ALLOW_REFRESH": False,
    # "JWT_REFRESH_EXPIRATION_DELTA": datetime.timedelta(days=7),
    # "JWT_AUTH_HEADER_PREFIX": "JWT",
    # "JWT_SECRET_KEY": SECRET_KEY,
    # "JWT_DECODE_HANDLER": "rest_framework_jwt.utils.jwt_decode_handler",
    # Keys will be set in core.apps.Config.ready()
    # "JWT_PUBLIC_KEY": "?",
    # 'JWT_PRIVATE_KEY': wallet.get_private(),
    # 'JWT_PRIVATE_KEY': None,
    # "JWT_ALGORITHM": "RS256",
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Bitcaster API",
    "DESCRIPTION": "",
    "VERSION": VERSION,
    "SERVE_INCLUDE_SCHEMA": False,
    # OTHER SETTINGS
    "SWAGGER_UI_DIST": "SIDECAR",  # shorthand to use the sidecar instead
    "SWAGGER_UI_FAVICON_HREF": "SIDECAR",
    "REDOC_DIST": "SIDECAR",
}
