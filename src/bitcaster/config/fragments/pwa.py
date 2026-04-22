PWA_APP_SUFFIX = ""

PWA_APP_NAME = "Bitcaster"
PWA_APP_DESCRIPTION = "Bitcaster Notification Console"
PWA_APP_THEME_COLOR = "#dc2626"
PWA_APP_BACKGROUND_COLOR = "#ffffff"
PWA_APP_DISPLAY = "standalone"
PWA_APP_DEBUG_MODE = True
PWA_APP_SCOPE = "/pwa/"
PWA_APP_ORIENTATION = "any"
PWA_APP_START_URL = "/pwa/"
PWA_APP_STATUS_BAR_COLOR = "default"
PWA_APP_ICONS = [
    {"src": "/static/bitcaster/images/logos/bitcaster.svg", "sizes": "any", "type": "image/svg+xml", "purpose": "any"},
    {"src": "/static/bitcaster/images/logos/logo48.png", "sizes": "48x48", "type": "image/png", "purpose": "any"},
    {"src": "/static/bitcaster/images/logos/logo128.png", "sizes": "128x128", "type": "image/png", "purpose": "any"},
    {"src": "/static/bitcaster/images/logos/logo400.png", "sizes": "400x400", "type": "image/png", "purpose": "any"},
    {"src": "/static/bitcaster/images/logos/logo500.png", "sizes": "512x512", "type": "image/png", "purpose": "any"},
    {
        "src": "/static/bitcaster/images/logos/logo500.png",
        "sizes": "512x512",
        "type": "image/png",
        "purpose": "maskable",
    },
]
PWA_APP_ICONS_APPLE = [{"src": "/static/bitcaster/images/logos/logo128.png", "sizes": "128x128", "type": "image/png"}]
PWA_APP_SPLASH_SCREEN = [
    {
        "src": "/static/bitcaster/images/logos/logo.png",
        "media": "(device-width: 320px) and (device-height: 568px) and (-webkit-device-pixel-ratio: 2)",
    }
]
PWA_APP_DIR = "ltr"
PWA_APP_LANG = "en-US"
