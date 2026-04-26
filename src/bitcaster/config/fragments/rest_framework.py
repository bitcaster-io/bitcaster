from typing import Any

from bitcaster import VERSION

REST_FRAMEWORK: dict[str, Any] = {
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

JWT_AUTH: dict[str, Any] = {}

SPECTACULAR_SETTINGS = {
    "TITLE": "Bitcaster API",
    "DESCRIPTION": """
Bitcaster is a system-to-user signal-to-message notification system.

It receives signals from your applications via REST API and distributes them as messages through various channels (Email, SMS, Push, etc.).
Messages are customized using a flexible template system, empowering users to manage their own notification preferences.

### ⚖️ Licensing & Terms
This API is subject to the **Bitcaster Source License (BSL-1.1)**.
Key restrictions:
* **Non-Compete:** Permanent prohibition on using Bitcaster to create competing commercial products or services.
* **Professional Use:** Allowed only as a backend connector for your own systems to notify your clients.
* **Client Systems:** Usage to process triggers from client systems or to provide internal messaging for clients is strictly prohibited.
* **Multi-Tenancy:** Multiple Organizations are allowed for internal operational needs only.

For full license details, please refer to the LICENSE file in the repository.
    """,
    "TERMS_OF_SERVICE": "https://www.bitcaster.io/terms/",
    "CONTACT": {
        "name": "Bitcaster Support",
        "url": "https://www.bitcaster.io/",
        "email": "info@bitcaster.io",
    },
    "LICENSE": {
        "name": "Bitcaster Source License 1.1 (BSL-1.1)",
    },
    "VERSION": VERSION,
    "SERVE_INCLUDE_SCHEMA": False,
    "SWAGGER_UI_DIST": "SIDECAR",
    "SWAGGER_UI_FAVICON_HREF": "SIDECAR",
    "REDOC_DIST": "SIDECAR",
}
